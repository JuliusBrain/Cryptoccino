"""Generate the /tv/ "Market Context" blurb — a short plain-English read on
current crypto conditions, written by Claude from live market data.

Run every 6h by .github/workflows/context.yml, which publishes the result to the
`news-data` branch; the terminal fetches it from raw.githubusercontent.com and
renders it between the daily brief and the news rail.

Cheapest model only (Haiku), tiny output, compact prompt — this is a low-token
job by design. Fully fail-open: if the data or the model call fails, keep the
last good blurb (cached at assets/data/market_context.json) rather than raising.

Usage: python -m pipeline.market_context [OUTPUT_PATH]
"""

import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import requests

from pipeline.cache import read_json, write_json
from pipeline.prices import fetch_prices
from pipeline.sentiment import fetch_fng

logger = logging.getLogger(__name__)

CACHE_PATH = Path("assets/data/market_context.json")
GLOBAL_ENDPOINT = "https://api.coingecko.com/api/v3/global"
REQUEST_TIMEOUT_S = 20

MODEL = "claude-haiku-4-5-20251001"   # cheapest model the project uses; no fallback
MAX_ATTEMPTS = 3
BACKOFF_BASE_S = 2
MAX_OUTPUT_TOKENS = 256

SYSTEM_PROMPT = (
    "You write the 'Market Context' line for a crypto terminal. Given a few market "
    "figures, write 2-3 plain-English sentences explaining what they imply about the "
    "current market mood. Be concrete and calm — no hype, no emojis, no financial "
    "advice, no preamble. Output only the sentences."
)


def _fetch_global():
    """BTC dominance %, total mcap (USD), 24h volume (USD) — or {} on failure."""
    headers = {"Accept": "application/json"}
    key = os.getenv("COINGECKO_KEY")
    if key:
        headers["x-cg-demo-api-key"] = key
    try:
        resp = requests.get(GLOBAL_ENDPOINT, headers=headers, timeout=REQUEST_TIMEOUT_S)
        resp.raise_for_status()
        d = resp.json().get("data") or {}
    except Exception as exc:
        logger.warning("Global fetch failed: %s: %s", exc.__class__.__name__, exc)
        return {}
    return {
        "dominance": (d.get("market_cap_percentage") or {}).get("btc"),
        "mcap": (d.get("total_market_cap") or {}).get("usd"),
        "volume": (d.get("total_volume") or {}).get("usd"),
    }


def _build_prompt(prices, fng, glob):
    """Compact list of the key figures — small to keep input tokens low."""
    lines = []
    for p in (prices or [])[:4]:   # BTC/ETH/BNB/SOL is plenty of context
        lines.append(f"{p['ticker']}: ${p['price']:,.0f} ({p['change_24h']:+.1f}% 24h)")
    if fng and fng.get("today") is not None:
        delta = fng.get("delta")
        d = f"{delta:+d} over 7d" if delta is not None else "7d change unknown"
        lines.append(f"Fear & Greed: {fng['today']} ({fng.get('today_label', '')}), {d}")
    if glob.get("dominance") is not None:
        lines.append(f"BTC dominance: {glob['dominance']:.1f}%")
    if glob.get("volume"):
        lines.append(f"24h total volume: ${glob['volume'] / 1e9:.0f}B")
    return "Market figures right now:\n" + "\n".join(lines)


def _ask_claude(user_message):
    """One-shot Haiku call with the same retry/backoff idiom as curate(); returns
    the blurb text, or raises after exhausting attempts."""
    client = anthropic.Anthropic(max_retries=0)
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            text = response.content[0].text.strip()
            usage = getattr(response, "usage", None)
            if usage is not None:
                logger.info(
                    "market_context: ok (in=%s, out=%s tokens).",
                    getattr(usage, "input_tokens", "?"), getattr(usage, "output_tokens", "?"),
                )
            return text
        except anthropic.APIStatusError as exc:
            code = getattr(exc, "status_code", None)
            if code is not None and code < 500 and code != 529:
                raise   # auth/config error — fail fast, don't burn retries
            last_exc = exc
        except (anthropic.RateLimitError, anthropic.APIConnectionError,
                anthropic.InternalServerError) as exc:
            last_exc = exc
        logger.warning("market_context: attempt %d/%d failed: %s",
                       attempt, MAX_ATTEMPTS, last_exc)
        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_BASE_S * 2 ** (attempt - 1))
    raise last_exc


def build_context():
    """Return {text, ts, generated} or the cached blurb on any failure (fail-open)."""
    try:
        prices = fetch_prices()
        fng = fetch_fng()
        glob = _fetch_global()
        if not prices and not fng:
            logger.warning("No market data; keeping cached context.")
            return read_json(CACHE_PATH)
        text = _ask_claude(_build_prompt(prices, fng, glob))
        if not text:
            return read_json(CACHE_PATH)
        now = datetime.now(timezone.utc)
        return {"text": text, "ts": int(now.timestamp()), "generated": now.isoformat()}
    except Exception as exc:
        logger.warning("Market context generation failed: %s: %s. Keeping cache.",
                       exc.__class__.__name__, exc)
        return read_json(CACHE_PATH)


def main(out_path=CACHE_PATH):
    out_path = Path(out_path)
    ctx = build_context()
    if ctx:
        write_json(out_path, ctx)
        print(f"Wrote market context to {out_path}")
    else:
        print("No context generated and no cache; nothing written.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    main(sys.argv[1] if len(sys.argv) > 1 else CACHE_PATH)
