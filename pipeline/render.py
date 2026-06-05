"""Render a curated issue dict + market list into a dated Jekyll post under _posts/.

The body is markdown with kramdown block-IAL hints ({: .pour}, {: .last-sip},
{: .kicker}, {: .brewing-label}) so the layout can target specific blocks
without rewriting markup. The price strip is the one inline-HTML island.
Filename convention: _posts/YYYY-MM-DD-cryptoccino.md.
"""

from datetime import date
from pathlib import Path

POSTS_DIR = "_posts"
TITLE_BASE = "Cryptoccino"


def _format_price(price):
    if price is None:
        return "0"
    if price >= 100:
        return f"{price:,.0f}"
    if price >= 1:
        return f"{price:.2f}"
    return f"{price:.4g}"


def _render_source_tags(links):
    if not links:
        return ""
    return " ".join(f"[`{link['source_id']}`]({link['url']})" for link in links)


def _render_pour(issue):
    lines = [f"> **The Pour.** {issue['pour']}"]
    today = issue.get("today") or []
    if today:
        parts = [f"{t['teaser']} _{t['beat']}_" for t in today]
        lines.append(">")
        lines.append(f"> **Today.** {' · '.join(parts)}.")
    lines.append("{: .pour}")
    return "\n".join(lines)


def _render_prices(markets):
    chips = []
    for coin in markets:
        change = coin.get("change_24h") or 0
        direction = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else "−"
        chips.append(
            f'    <li class="chip">'
            f'<span class="ticker">{coin["symbol"]}</span>'
            f'<span class="price">{_format_price(coin.get("price"))}</span>'
            f'<span class="change {direction}">{sign}{abs(change):.2f}%</span>'
            f"</li>"
        )
    return (
        '<section class="prices">\n'
        '  <p class="prices-label">Prices</p>\n'
        '  <ul class="chips">\n'
        + "\n".join(chips)
        + "\n  </ul>\n"
        "</section>"
    )


def _render_lead(lead):
    parts = ['<section class="lead" markdown="1">', ""]
    parts.append(f"**{lead['kicker']}**")
    parts.append("{: .kicker}")
    parts.append("")
    parts.append(f"## {lead['headline']}")
    parts.append("")
    source_tags = _render_source_tags(lead.get("links") or [])
    if source_tags:
        parts.append(source_tags)
        parts.append("{: .sources}")
        parts.append("")
    for block in lead.get("blocks") or []:
        parts.append(f"**{block['label']}.** {block['text']}")
        parts.append("")
    parts.append("</section>")
    return "\n".join(parts)


def _render_beat(beat):
    parts = [f"## {beat['title']}", ""]
    for item in beat.get("items") or []:
        sources = _render_source_tags(item.get("links") or [])
        suffix = f" {sources}" if sources else ""
        parts.append(f"> **{item['lead_in']}** {item['text']}{suffix}")
        parts.append("")
    return "\n".join(parts).rstrip()


def _render_brewing(brewing):
    parts = ["## What else is grinding?", "{: .brewing-label}", ""]
    for item in brewing:
        sources = _render_source_tags(item.get("links") or [])
        suffix = f" {sources}" if sources else ""
        parts.append(f"- {item['text']}{suffix}")
    return "\n".join(parts)


def _render_last_sip(issue):
    return (
        "---\n\n"
        f"> **Last sip.** {issue['last_sip']}\n"
        "{: .last-sip}"
    )


def _render_body(issue, markets):
    blocks = [_render_pour(issue)]

    if markets:
        blocks.append(_render_prices(markets))

    if issue.get("lead"):
        blocks.append(_render_lead(issue["lead"]))

    for beat in issue.get("beats") or []:
        blocks.append(_render_beat(beat))

    if issue.get("brewing"):
        blocks.append(_render_brewing(issue["brewing"]))

    blocks.append(_render_last_sip(issue))

    return "\n\n".join(blocks) + "\n"


def _yaml_quote(value):
    return '"' + (value or "").replace('"', '\\"') + '"'


def render_post(issue, markets=None, card_path=None):
    """Write today's Jekyll post from the curated dict + markets, return path.

    `card_path` is a site-relative path (e.g. /assets/cards/2026-06-05.png)
    that ends up in the post's front matter so the layout can emit the hero
    image and the og:image/twitter:image meta. None means no card today.
    """
    markets = markets or []
    today = date.today()
    iso = today.isoformat()
    long_date = today.strftime("%A %d %B %Y")
    title = f"{TITLE_BASE} — {long_date}"

    fm = [
        "---",
        "layout: issue",
        f"title: {_yaml_quote(title)}",
        f"date: {iso}",
        f"issue_date: {iso}",
        f"description: {_yaml_quote(issue.get('pour'))}",
    ]
    if card_path:
        fm.append(f"card: {card_path}")
    fm.append("---")
    fm.append("")
    fm.append("")
    front_matter = "\n".join(fm)

    out_path = Path(POSTS_DIR) / f"{iso}-cryptoccino.md"
    out_path.write_text(front_matter + _render_body(issue, markets))
    return str(out_path)
