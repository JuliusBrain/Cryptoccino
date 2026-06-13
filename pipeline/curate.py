"""Run one Claude call that turns the deduped item list into the day's issue.

Loads prompts/brief_system.md as the system prompt, formats the items as a
numbered list with source_id, title, summary, link, and age in hours, then
asks the model for a JSON document with: a one-line opener (pour), a 3-item
today teaser, an optional labelled lead, ordered beat roundups, a brewing
tail, and a closing line. Beats are reordered into canonical order and any
beat with no items is dropped before returning.

Primary model: claude-sonnet-4-6.
Cheaper fallback: claude-haiku-4-5-20251001.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

from pipeline import llm

logger = logging.getLogger(__name__)

# Primary first, cheaper fallback second; llm.call() retries each with backoff
# then falls through. Names kept here for callers/tests that import them.
MODELS = [llm.SONNET, llm.HAIKU]
MAX_ATTEMPTS_PER_MODEL = llm.MAX_ATTEMPTS
_strip_fences = llm.strip_fences   # re-export so existing imports keep working
SYSTEM_PROMPT_PATH = "prompts/brief_system.md"
CONFIG_PATH = "config/feeds.yaml"
CANONICAL_BEATS = ["the_tape", "projects_money", "security_desk", "on_the_hill"]
MAX_OUTPUT_TOKENS = 16384   # headroom so a busy day's issue doesn't truncate mid-JSON

JSON_SHAPE_EXAMPLE = {
    "pour": "one dry line on the mood of the day",
    "today": [
        {"teaser": "short teaser phrase", "beat": "Markets"},
        {"teaser": "another teaser", "beat": "Security Desk"},
        {"teaser": "third teaser", "beat": "Projects & Money"},
    ],
    "lead": {
        "kicker": "MARKETS",
        "headline": "Single most important story of the day.",
        "links": [
            {"source_id": "theblock", "url": "https://..."},
            {"source_id": "coindesk", "url": "https://..."},
        ],
        "blocks": [
            {"label": "What happened", "text": "Two to three sentences."},
            {"label": "Why it matters", "text": "Two to three sentences."},
            {"label": "The catch", "text": "Two to three sentences."},
        ],
    },
    "beats": [
        {
            "id": "the_tape",
            "title": "Markets",
            "items": [
                {
                    "lead_in": "Bold lead-in phrase.",
                    "text": "Two to three self-contained sentences.",
                    "links": [
                        {"source_id": "coindesk", "url": "https://..."},
                    ],
                }
            ],
        }
    ],
    "brewing": [
        {
            "text": "Single-sentence note on a minor story.",
            "links": [{"source_id": "decrypt", "url": "https://..."}],
        }
    ],
    "last_sip": "one quiet unresolved line",
}


def _build_user_message(items, max_per_beat, max_age_hours, fng=None):
    now = datetime.now(timezone.utc)
    lines = [
        f"You are given {len(items)} news items from the last {max_age_hours} hours.",
        "",
        "Output requirements:",
        "- ONE lead (or null on a quiet day) with 2 to 4 labelled blocks. Third label flexes between 'The catch' and 'Watch'.",
        f"- Beat roundups, capped at {max_per_beat} items each. Skip empty beats. Each item: a bold lead_in phrase and 2 to 3 self-contained sentences.",
        "- 3 to 6 brewing items, each a single sentence.",
        "- 'today' is exactly 3 teasers naming the 3 biggest items with their beat title (display title, e.g. 'Markets').",
        "- 'links' is an array so clustered duplicates surface every source.",
        "",
        f"Beat ids must be one of: {', '.join(CANONICAL_BEATS)}.",
        "",
        "Return ONLY valid JSON, no markdown fences, in this exact shape:",
        json.dumps(JSON_SHAPE_EXAMPLE, indent=2),
        "",
    ]
    if fng and fng.get("today") is not None:
        delta_str = (
            f"{fng['delta']:+d}" if fng.get("delta") is not None else "unknown"
        )
        lines.append(
            f"Sentiment context (Crypto Fear & Greed Index): "
            f"today {fng['today']} ({fng.get('today_label', '')}), "
            f"7-day delta {delta_str}. "
            "Cite it once in a lead block when it strengthens the counter-narrative; "
            "skip if it doesn't add."
        )
        lines.append("")
    lines.append("Items:")
    for i, item in enumerate(items, 1):
        age_h = int((now - item["published"]).total_seconds() // 3600)
        lines.append(
            f"{i}. [{item['source_id']}] {item['title']}\n"
            f"   summary: {item['summary']}\n"
            f"   link: {item['link']}\n"
            f"   age: {age_h}h"
        )
    return "\n".join(lines)


def _reorder_beats(beats):
    # Model output is untrusted: skip any beat missing an id rather than
    # KeyError-aborting an otherwise-publishable (and already-billed) run.
    by_id = {b["id"]: b for b in beats if isinstance(b, dict) and b.get("id")}
    return [
        by_id[beat_id]
        for beat_id in CANONICAL_BEATS
        if by_id.get(beat_id) and by_id[beat_id].get("items")
    ]


def curate(items, fng=None):
    """Run one Claude call and return the parsed issue as a dict.

    `fng` (optional) is the dict from pipeline.sentiment.fetch_fng. When
    supplied, today's value + 7-day delta are included in the user message
    so the model can cite it in a lead block when relevant.
    """
    system_prompt = Path(SYSTEM_PROMPT_PATH).read_text()
    config = yaml.safe_load(Path(CONFIG_PATH).read_text())
    max_per_beat = config["meta"]["max_per_beat"]
    max_age_hours = config["meta"]["max_age_hours"]

    user_message = _build_user_message(items, max_per_beat, max_age_hours, fng=fng)

    # Sonnet first, Haiku fallback; the shared helper retries each model with
    # backoff. A malformed-JSON response is retryable (parse runs inside the
    # loop); auth/config errors fail fast. Raises if every model is exhausted —
    # curate has no fail-open, so the run fails rather than publish nothing.
    result = llm.call(
        MODELS, system_prompt, user_message, MAX_OUTPUT_TOKENS,
        parse=lambda raw: json.loads(_strip_fences(raw)),
    )
    result["beats"] = _reorder_beats(result.get("beats") or [])
    return result


if __name__ == "__main__":
    from pipeline.ingest import fetch_feeds
    from pipeline.store import filter_new, init_db

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    init_db()
    items = fetch_feeds()
    new = filter_new(items)
    print(f"\nCurating {len(new)} new items...\n")
    issue = curate(new)
    print(json.dumps(issue, indent=2, ensure_ascii=False))
