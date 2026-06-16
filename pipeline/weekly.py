"""Weekly recap — one Sonnet pass that picks the biggest stories of the past week
from the last 7 daily issues and writes a short recap.

Source is the already-curated `beats[].items[]` front matter of the recent daily
posts (no re-ingest, no DB). The model returns INDICES into that list, so each
recap entry deep-links to the real source issue (/YYYY/MM/DD/#slug) — never a
hallucinated link. Output is a dated entry in the `weekly` Jekyll collection
(_weekly/<week-end>.md), browsable at /weekly/. Fails loudly rather than publish
an empty recap; skips if the week's recap already exists.

Usage: python -m pipeline.weekly
"""

import glob
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

from pipeline import llm
from pipeline.render import _esc, _esc_attr

logger = logging.getLogger(__name__)

POSTS_DIR = "_posts"
WEEKLY_DIR = "_weekly"
SYSTEM_PROMPT_PATH = "prompts/weekly_system.md"
N_ISSUES = 7
MAX_STORIES = 8
MAX_OUTPUT_TOKENS = 4096


def _parse_front_matter(path):
    """Return the YAML front-matter dict of a Jekyll file, or None."""
    text = Path(path).read_text()
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def _as_date(value):
    """Coerce a front-matter date (date / datetime / 'YYYY-MM-DD' str) to date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _issue_url(d):
    """Permalink for a daily issue (config permalink: /:year/:month/:day/)."""
    return f"/{d.year:04d}/{d.month:02d}/{d.day:02d}/"


def _week_stories(n=N_ISSUES):
    """Flatten the beats items of the newest `n` daily issues into one list, each
    tagged with its source date / issue URL / anchor slug."""
    paths = sorted(glob.glob(f"{POSTS_DIR}/*-cryptoccino.md"))[-n:]
    stories = []
    for p in paths:
        fm = _parse_front_matter(p)
        if not fm:
            continue
        d = _as_date(fm.get("date"))
        if d is None:
            continue
        url = _issue_url(d)
        for beat in (fm.get("beats") or []):
            beat_title = beat.get("title", "")
            for it in (beat.get("items") or []):
                lead_in = (it.get("lead_in") or "").strip()
                slug = (it.get("slug") or "").strip()
                if not lead_in or not slug:
                    continue
                stories.append({
                    "date": d,
                    "issue_url": url,
                    "beat_title": beat_title,
                    "lead_in": lead_in,
                    "text": (it.get("text") or "").strip(),
                    "slug": slug,
                })
    return stories


def _build_prompt(stories):
    lines = [
        f"{i}. [{s['date'].strftime('%a %d %b')} · {s['beat_title']}] {s['lead_in']}\n"
        f"   {s['text']}"
        for i, s in enumerate(stories, 1)
    ]
    return "This week's stories from the daily briefs:\n\n" + "\n".join(lines)


def _ask_claude(user_message):
    """One Sonnet call returning {intro, stories:[{i, why}]}, or raising."""
    system = Path(SYSTEM_PROMPT_PATH).read_text()
    return llm.call(
        [llm.SONNET], system, user_message, MAX_OUTPUT_TOKENS,
        parse=lambda raw: json.loads(llm.strip_fences(raw)),
    )


def build_recap(stories):
    """Map the model's chosen indices back to real stories (deep-linked to their
    source issue). Returns {intro, stories:[{headline, why, link, date}]}."""
    parsed = _ask_claude(_build_prompt(stories))
    out, seen = [], set()
    for e in (parsed.get("stories") or [])[:MAX_STORIES]:
        i = e.get("i")
        if not isinstance(i, int) or not (1 <= i <= len(stories)) or i in seen:
            continue  # drop out-of-range / duplicate indices
        seen.add(i)
        s = stories[i - 1]
        out.append({
            "headline": s["lead_in"],
            "why": (e.get("why") or "").strip(),
            "link": s["issue_url"] + "#" + s["slug"],
            "date": s["date"],
        })
    return {"intro": (parsed.get("intro") or "").strip(), "stories": out}


def _render_body(recap):
    parts = []
    if recap["intro"]:
        parts.append('<p class="weekly-intro">' + _esc(recap["intro"]) + "</p>\n")
    parts.append('<ol class="weekly-list">\n')
    for s in recap["stories"]:
        parts.append(
            '  <li class="weekly-item">'
            f'<a class="weekly-link" href="{_esc_attr(s["link"])}">'
            f'<span class="weekly-item__head">{_esc(s["headline"])}</span></a>'
            + (f'<span class="weekly-why">{_esc(s["why"])}</span>' if s["why"] else "")
            + f'<span class="weekly-date">{_esc(s["date"].strftime("%-d %b"))}</span>'
            "</li>\n"
        )
    parts.append("</ol>\n")
    return "".join(parts)


def render_weekly(recap, stories, out_dir=WEEKLY_DIR):
    dates = [s["date"] for s in stories]
    week_start, week_end = min(dates), max(dates)
    front = {
        "title": f"Weekly Recap — {week_start.strftime('%-d %b')}–{week_end.strftime('%-d %b %Y')}",
        "date": week_end.isoformat(),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "description": (recap["intro"] or "The week's biggest crypto stories.")[:200],
    }
    fm = yaml.safe_dump(front, default_flow_style=False, allow_unicode=True, sort_keys=False)
    content = (
        '<section class="archive-page weekly-page">\n'
        '  <header class="archive-head">\n'
        '    <p class="archive-eyebrow">● The week in review</p>\n'
        f'    <h1>{_esc(front["title"])}</h1>\n'
        '  </header>\n'
        + _render_body(recap)
        + '</section>\n'
    )
    out_path = Path(out_dir) / f"{week_end.isoformat()}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("---\n" + fm + "---\n\n" + content)
    return out_path


def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    stories = _week_stories()
    if not stories:
        logger.error("No daily issues found; nothing to recap.")
        sys.exit(1)
    week_end = max(s["date"] for s in stories)
    out_path = Path(WEEKLY_DIR) / f"{week_end.isoformat()}.md"
    if out_path.exists():
        print(f"Weekly recap {out_path} already exists; skipping.")
        return
    recap = build_recap(stories)
    if not recap["stories"]:
        logger.error("Model selected zero stories from %d candidates; refusing to "
                     "publish an empty recap.", len(stories))
        sys.exit(1)
    path = render_weekly(recap, stories)
    print(f"Wrote {path} ({len(recap['stories'])} stories).")


if __name__ == "__main__":
    main()
