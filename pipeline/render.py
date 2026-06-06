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


def _render_fng_chip(fng):
    """Small Fear & Greed Index chip — current value, classification, 7d delta."""
    if not fng or fng.get("today") is None:
        return ""
    today = fng["today"]
    label = fng.get("today_label") or ""
    delta = fng.get("delta")
    if delta is None:
        delta_html = ""
    else:
        direction = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        sign = "+" if delta > 0 else ("−" if delta < 0 else "±")
        delta_html = (
            f' <span class="fng-delta {direction}">{sign}{abs(delta)} / 7d</span>'
        )
    return (
        '<div class="fng-chip" aria-label="Crypto Fear & Greed Index">'
        '<span class="fng-label">F&amp;G</span>'
        f'<span class="fng-value">{today}</span>'
        f'<span class="fng-class">{label}</span>'
        f'{delta_html}'
        '</div>'
    )


def _render_lead(lead, fng=None):
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
    fng_chip = _render_fng_chip(fng)
    if fng_chip:
        parts.append(fng_chip)
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


# (threshold, label, bean count) — strictly-less-than thresholds in ascending
# order. max(abs(change_24h)) across the price strip determines the bucket.
MOOD_LEVELS = [
    (2.0,  "Decaf morning", 1),
    (4.0,  "Single shot",   2),
    (6.0,  "House blend",   3),
    (9.0,  "Dark roast",    4),
    (None, "Extra bold",    5),  # >= 9% catch-all
]

_BEAN_SVG = (
    '<svg class="bean" viewBox="0 0 14 18" width="14" height="18" aria-hidden="true">'
    '<ellipse class="bean-body" cx="7" cy="9" rx="6" ry="8.5"/>'
    '<path class="bean-seam" d="M 7 1 C 5 5 5 13 7 17" fill="none"/>'
    "</svg>"
)


def _render_mood_gauge(prices):
    """1-5 coffee-bean strength meter keyed to today's max price move."""
    if not prices:
        return ""
    top = max(prices, key=lambda p: abs(p.get("change_24h") or 0))
    max_move = abs(top.get("change_24h") or 0)
    label, beans = next(
        (lbl, n) for thresh, lbl, n in MOOD_LEVELS if thresh is None or max_move < thresh
    )
    beans_html = "".join(
        f'<span class="{"bean-filled" if i < beans else "bean-empty"}">{_BEAN_SVG}</span>'
        for i in range(5)
    )
    return (
        '<div class="mood-gauge" role="meter" aria-label="Market mood" '
        f'aria-valuemin="1" aria-valuemax="5" aria-valuenow="{beans}" '
        f'aria-valuetext="{label}">\n'
        '  <p class="mood-label">Today\'s Roast</p>\n'
        f'  <div class="mood-beans">{beans_html}</div>\n'
        f'  <p class="mood-detail"><strong>{label}</strong> · top move '
        f'{max_move:.1f}% ({top["ticker"]})</p>\n'
        "</div>"
    )


def _render_body(issue, prices, section_cards=None, fng=None):
    section_cards = section_cards or {}
    prices_html = render_strip_html(prices, mode="web") if prices else ""
    blocks = []
    mood_html = _render_mood_gauge(prices)
    if mood_html:
        blocks.append(mood_html)
    blocks.append(_render_pour(issue, prices_html=prices_html))

    if issue.get("lead"):
        blocks.append(_render_lead(issue["lead"], fng=fng))

    for beat in issue.get("beats") or []:
        blocks.append(_render_beat(beat, section_cards.get(beat.get("id"))))

    if issue.get("brewing"):
        blocks.append(_render_brewing(issue["brewing"]))

    blocks.append(_render_last_sip(issue))

    return "\n\n".join(blocks) + "\n"


def _yaml_quote(value):
    return '"' + (value or "").replace('"', '\\"') + '"'


def render_post(
    issue, prices=None, card_path=None, section_cards=None, fng=None
):
    """Write today's Jekyll post from the curated dict + prices, return path.

    `prices` is the list from pipeline.prices.fetch_prices (or None on a
    failed fetch with no cache). `card_path` lands in front matter so the
    layout emits the hero image + og:image. `section_cards` maps beat_id
    to a site-relative path; each banner replaces the corresponding H2.
    `fng` is the dict from pipeline.sentiment.fetch_fng (or None); when
    supplied, a small chip is rendered inside the lead section.
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
        front_matter
        + _render_body(issue, prices, section_cards=section_cards, fng=fng)
    )
    return str(out_path)
