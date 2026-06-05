"""Render a curated issue dict into a dated Jekyll post under _posts/.

Filename convention: _posts/YYYY-MM-DD-cryptoccino.md.
"""

from datetime import date
from pathlib import Path

POSTS_DIR = "_posts"
TITLE_BASE = "Cryptoccino"


def _render_body(issue):
    parts = [f"> **The Pour.** {issue['pour']}", ""]
    for beat in issue["beats"]:
        parts.append(f"## {beat['title']}")
        parts.append("")
        for story in beat["stories"]:
            parts.append(f"**[{story['headline']}]({story['link']})** `{story['source_id']}`")
            parts.append("")
            parts.append(story["body"])
            parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"> **Last sip.** {issue['last_sip']}")
    parts.append("")
    return "\n".join(parts)


def render_post(issue):
    """Write today's Jekyll post from the curated dict and return its path."""
    today = date.today()
    iso = today.isoformat()
    long_date = today.strftime("%A %d %B %Y")
    title = f"{TITLE_BASE} — {long_date}"

    front_matter = (
        "---\n"
        "layout: issue\n"
        f'title: "{title}"\n'
        f"date: {iso}\n"
        f"issue_date: {iso}\n"
        "---\n\n"
    )

    out_path = Path(POSTS_DIR) / f"{iso}-cryptoccino.md"
    out_path.write_text(front_matter + _render_body(issue))
    return str(out_path)
