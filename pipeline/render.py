"""Render a curated issue dict + market list into a dated Jekyll post under _posts/.

The body is markdown with kramdown block-IAL hints ({: .pour}, {: .last-sip},
{: .kicker}, {: .brewing-label}) so the layout can target specific blocks
without rewriting markup. The price strip is the one inline-HTML island.
Filename convention: _posts/YYYY-MM-DD-cryptoccino.md.
"""

from datetime import date
from pathlib import Path

from pipeline.prices import render_strip_html

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


def _render_pour(issue, prices_html=""):
    """Render the Pour blockquote, wrapped in a band that also contains
    the price strip when one is supplied."""
    pour_lines = [f"> **The Pour.** {issue['pour']}"]
    today = issue.get("today") or []
    if today:
        parts = [f"{t['teaser']} _{t['beat']}_" for t in today]
        pour_lines.append(">")
        pour_lines.append(f"> **Today.** {' · '.join(parts)}.")
    pour_lines.append("{: .pour}")
    pour_md = "\n".join(pour_lines)

    band = ['<div class="pour-band" markdown="1">', "", pour_md, ""]
    if prices_html:
        band.append(prices_html)
        band.append("")
    band.append("</div>")
    return "\n".join(band)


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


def _render_beat(beat, section_card_path=None):
    parts = []
    if section_card_path:
        title = beat.get("title", "")
        # Liquid expression so Jekyll prepends site.baseurl at build time
        # (the path stored in section_cards is baseurl-relative).
        # The banner carries the beat name visually, so the H2 is dropped
        # when a card is present to avoid duplicate labels.
        parts.append(
            f'<img class="section-card" '
            f'src="{{{{ "{section_card_path}" | relative_url }}}}" '
            f'alt="{title}">'
        )
        parts.append("")
    else:
        # Fallback when card generation failed — beat is never unlabelled.
        parts.append(f"## {beat['title']}")
        parts.append("")
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


def _render_body(issue, prices, section_cards=None):
    section_cards = section_cards or {}
    prices_html = render_strip_html(prices, mode="web") if prices else ""
    blocks = [_render_pour(issue, prices_html=prices_html)]

    if issue.get("lead"):
        blocks.append(_render_lead(issue["lead"]))

    for beat in issue.get("beats") or []:
        blocks.append(_render_beat(beat, section_cards.get(beat.get("id"))))

    if issue.get("brewing"):
        blocks.append(_render_brewing(issue["brewing"]))

    blocks.append(_render_last_sip(issue))

    return "\n\n".join(blocks) + "\n"


def _yaml_quote(value):
    return '"' + (value or "").replace('"', '\\"') + '"'


def render_post(issue, prices=None, card_path=None, section_cards=None):
    """Write today's Jekyll post from the curated dict + prices, return path.

    `prices` is the list from pipeline.prices.fetch_prices (or None on a
    failed fetch with no cache). `card_path` lands in front matter so the
    layout emits the hero image + og:image. `section_cards` maps beat_id
    to a site-relative path; each banner replaces the corresponding H2.
    """
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
    out_path.write_text(
        front_matter + _render_body(issue, prices, section_cards=section_cards)
    )
    return str(out_path)
