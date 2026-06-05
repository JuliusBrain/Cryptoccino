"""Run one Claude call that turns the deduped item list into the day's issue.

Loads prompts/brief_system.md as the system prompt, formats the items as a
numbered list with source_id, title, summary, link, and age in hours, then
asks the model for a JSON document with a one-line opener, ordered beats,
and a closing line. Beats are reordered into canonical order and any beat
with no stories is dropped before returning.

Primary model: claude-sonnet-4-6.
Cheaper fallback: claude-haiku-4-5-20251001.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import yaml

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT_PATH = "prompts/brief_system.md"
CONFIG_PATH = "config/feeds.yaml"
CANONICAL_BEATS = ["the_tape", "projects_money", "security_desk", "on_the_hill"]
MAX_OUTPUT_TOKENS = 8192

JSON_SHAPE_EXAMPLE = {
    "pour": "one dry line",
    "beats": [
        {
            "id": "the_tape",
            "title": "The Tape",
            "stories": [
                {
                    "headline": "...",
                    "body": "...",
                    "source_id": "coindesk",
                    "link": "https://...",
                }
            ],
        }
    ],
    "last_sip": "one quiet line",
}


def _build_user_message(items, max_per_beat, max_age_hours):
    now = datetime.now(timezone.utc)
    lines = [
        f"You are given {len(items)} news items from the last {max_age_hours} hours.",
        f"Cap each beat at {max_per_beat} stories. Skip a beat entirely if nothing earns a slot.",
        "",
        "Return ONLY valid JSON, no markdown fences, in this exact shape:",
        json.dumps(JSON_SHAPE_EXAMPLE, indent=2),
        "",
        f"Beat ids must be one of: {', '.join(CANONICAL_BEATS)}.",
        "",
        "Items:",
    ]
    for i, item in enumerate(items, 1):
        age_h = int((now - item["published"]).total_seconds() // 3600)
        lines.append(
            f"{i}. [{item['source_id']}] {item['title']}\n"
            f"   summary: {item['summary']}\n"
            f"   link: {item['link']}\n"
            f"   age: {age_h}h"
        )
    return "\n".join(lines)


def _strip_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()


def _reorder_beats(beats):
    by_id = {b["id"]: b for b in beats}
    return [
        by_id[beat_id]
        for beat_id in CANONICAL_BEATS
        if by_id.get(beat_id) and by_id[beat_id].get("stories")
    ]


def curate(items):
    """Run one Claude call and return the parsed issue as a dict."""
    system_prompt = Path(SYSTEM_PROMPT_PATH).read_text()
    config = yaml.safe_load(Path(CONFIG_PATH).read_text())
    max_per_beat = config["meta"]["max_per_beat"]
    max_age_hours = config["meta"]["max_age_hours"]

    user_message = _build_user_message(items, max_per_beat, max_age_hours)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    raw = response.content[0].text

    try:
        result = json.loads(_strip_fences(raw))
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON. Raw response:\n%s", raw)
        raise

    result["beats"] = _reorder_beats(result["beats"])
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
