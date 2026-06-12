"""Generate the /tv/ news digest — recent headlines deduped across sources and
sorted into Market / Business / Security / Policy by Claude, each with a short take.

Reuses pipeline.news.build_news for the candidate headlines, then makes one
cheap Haiku call to cluster cross-source duplicates, categorize, and write a
one-line take per kept story. Claude returns indices into the input list, so the
real link + source are looked up from our data (never hallucinated) and each
story points to exactly one source.

Published every ~3h to the `news-data` branch by .github/workflows/digest.yml;
the terminal fetches it from raw.githubusercontent.com. Fully fail-open: keeps
the last good digest if data or the model call fails.

Usage: python -m pipeline.news_digest [OUTPUT_PATH]
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from pipeline.cache import read_json, write_json
from pipeline.news import build_news

logger = logging.getLogger(__name__)

CACHE_PATH = Path("assets/data/news_digest.json")
CATEGORIES = ["market", "business", "security", "policy"]
MAX_CANDIDATES = 40
MAX_PER_CATEGORY = 5

MODEL = "claude-haiku-4-5-20251001"   # cheapest model; no fallback
MAX_ATTEMPTS = 3
BACKOFF_BASE_S = 2
MAX_OUTPUT_TOKENS = 1024

SYSTEM_PROMPT = (
    "You curate a live crypto news digest for a terminal. You are given numbered "
    "headlines, each with its source in brackets. Do three things:\n"
    "1. Collapse duplicates — headlines reporting the SAME event become one entry; "
    "keep the single best source.\n"
    "2. Sort entries into exactly these categories: market (prices, macro, trading, "
    "ETFs), business (launches, funding, deals, products, partnerships), security "
    "(hacks, exploits, scams, threats), policy (regulation, courts, government).\n"
    "3. For each kept entry write a 'take': a 6-14 word plain-English clause, calm, "
    "no hype, no period needed.\n"
    "Keep at most 5 per category, most important first; drop low-signal/off-topic "
    "items. Return ONLY JSON, no markdown fence, in this exact shape:\n"
    '{"market":[{"i":1,"take":"..."}],"business":[],"security":[],"policy":[]}\n'
    "where i is the chosen headline's number."
)


def _strip_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()


def _prompt(items):
    lines = [f"{i}. [{it['source']}] {it['title']}" for i, it in enumerate(items, 1)]
    return "Headlines:\n" + "\n".join(lines)


def _ask_claude(user_message):
    """One-shot Haiku call returning the parsed JSON, or raising after attempts."""
    client = anthropic.Anthropic(max_retries=0)
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            return json.loads(_strip_fences(resp.content[0].text))
        except anthropic.APIStatusError as exc:
            code = getattr(exc, "status_code", None)
            if code is not None and code < 500 and code != 529:
                raise  # auth/config error — fail fast
            last_exc = exc
        except (anthropic.RateLimitError, anthropic.APIConnectionError,
                anthropic.InternalServerError, json.JSONDecodeError) as exc:
            last_exc = exc
        logger.warning("digest: attempt %d/%d failed: %s", attempt, MAX_ATTEMPTS, last_exc)
        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_BASE_S * 2 ** (attempt - 1))
    raise last_exc


def build_digest():
    """Return {generated, ts, market:[...], ...} or the cached digest (fail-open)."""
    try:
        items = build_news()[:MAX_CANDIDATES]
        if not items:
            logger.warning("No candidate headlines; keeping cached digest.")
            return read_json(CACHE_PATH)
        parsed = _ask_claude(_prompt(items))
        now = datetime.now(timezone.utc)
        out = {"generated": now.isoformat(), "ts": int(now.timestamp())}
        for cat in CATEGORIES:
            entries = []
            for e in (parsed.get(cat) or [])[:MAX_PER_CATEGORY]:
                i = e.get("i")
                if not isinstance(i, int) or not (1 <= i <= len(items)):
                    continue  # ignore out-of-range / hallucinated indices
                src = items[i - 1]
                entries.append({
                    "headline": src["title"],   # real headline + link + one source
                    "take": (e.get("take") or "").strip(),
                    "source": src["source"],
                    "link": src["link"],
                })
            out[cat] = entries
        if not any(out[c] for c in CATEGORIES):
            return read_json(CACHE_PATH)   # empty digest → keep last good
        return out
    except Exception as exc:
        logger.warning("Digest generation failed: %s: %s. Keeping cache.",
                       exc.__class__.__name__, exc)
        return read_json(CACHE_PATH)


def main(out_path=CACHE_PATH):
    out_path = Path(out_path)
    digest = build_digest()
    if digest:
        write_json(out_path, digest)
        n = sum(len(digest.get(c, [])) for c in CATEGORIES)
        print(f"Wrote digest ({n} stories) to {out_path}")
    else:
        print("No digest generated and no cache; nothing written.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    main(sys.argv[1] if len(sys.argv) > 1 else CACHE_PATH)
