"""Render a curated issue dict + market list into a dated Jekyll post under _posts/.

The body is markdown with kramdown block-IAL hints ({: .pour}, {: .last-sip},
{: .kicker}, {: .brewing-label}) so the layout can target specific blocks
without rewriting markup. The price strip is the one inline-HTML island.
Filename convention: _posts/YYYY-MM-DD-cryptoccino.md.
"""

import html
import re
from datetime import date
from pathlib import Path

import yaml

from pipeline.prices import render_strip_html

POSTS_DIR = "_posts"
TITLE_BASE = "Cryptoccino"

# --- Output escaping -------------------------------------------------------
# The body is markdown that kramdown renders WITHOUT sanitizing raw HTML, and
# it carries strings derived from UNTRUSTED RSS feeds (relayed by the model,
# which is not a security boundary). So every model/feed-derived value is
# escaped at the point it enters the body: _esc for markdown/text and inline
# HTML text nodes, _esc_attr for HTML attribute values, and _safe_url to keep
# only http(s) link targets (blocks javascript:/data: scheme XSS).

_HTTP_URL = re.compile(r"(?i)^https?://")


def _no_liquid(text):
    """Neutralise Liquid delimiters so feed/model text can't inject template
    tags ({{ ... }}, {% ... %}) that Jekyll would execute at build time (SSTI).
    Breaking the leading brace is enough to disarm both tag forms; browsers
    render the entities back to literal { } in the page."""
    return text.replace("{", "&#123;").replace("}", "&#125;")


def _esc(value):
    """Escape a model/feed string for markdown body / HTML text-node context.
    NOT safe for HTML attribute values (doesn't escape quotes) — use _esc_attr."""
    return _no_liquid(html.escape(str(value or ""), quote=False))


def _esc_attr(value):
    """Escape a model/feed string for a double-quoted HTML attribute value."""
    return _no_liquid(html.escape(str(value or ""), quote=True))


def _safe_url(url):
    """Return the URL only if it is an http(s) link, else '' (drop it)."""
    url = str(url or "").strip()
    return url if _HTTP_URL.match(url) else ""


def _slugify(text):
    """A lowercase, hyphenated anchor slug from arbitrary text."""
    s = re.sub(r"[^\w\s-]", "", str(text or "").lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s or "story"


def _make_slugger():
    """Return a callable mapping text -> a slug unique within one issue
    (kramdown-style -2, -3 suffixes on collision)."""
    seen = {}

    def slug_for(text):
        base = _slugify(text)
        seen[base] = seen.get(base, 0) + 1
        return base if seen[base] == 1 else f"{base}-{seen[base]}"

    return slug_for


def _assign_slugs(beats, slugger=None):
    """Return a copy of `beats` with a unique per-issue `slug` on each item.
    Pass the issue-wide `slugger` (shared with the lead headline) so all ids are
    unique and identical to the in-body `{: #slug}` anchors — letting
    front-matter/beat-pages/search deep-link to the same stories."""
    slugger = slugger or _make_slugger()
    out = []
    for beat in beats or []:
        items = [
            {**item, "slug": slugger(item.get("lead_in", ""))}
            for item in beat.get("items") or []
        ]
        out.append({**beat, "items": items})
    return out


def _beats_front_matter(beats):
    """Serialize the slugged beats into a `beats:` YAML block for front matter
    (the structured data beat pages + search read). Empty string when no beats."""
    if not beats:
        return ""
    data = [
        {
            "id": beat.get("id", ""),
            "title": beat.get("title", ""),
            "items": [
                {
                    "lead_in": item.get("lead_in", ""),
                    "text": item.get("text", ""),
                    "slug": item["slug"],
                }
                for item in beat.get("items") or []
            ],
        }
        for beat in beats
    ]
    return yaml.safe_dump(
        {"beats": data}, allow_unicode=True, sort_keys=False, default_flow_style=False
    ).rstrip()


def _render_source_tags(links):
    if not links:
        return ""
    tags = []
    for link in links:
        # source_id sits in a kramdown code span + a markdown link label;
        # restrict to a safe allowlist so it can't perturb either structure.
        sid = re.sub(r"[^A-Za-z0-9._-]", "", str(link.get("source_id", "")))
        url = _safe_url(link.get("url"))
        tags.append(f"[`{sid}`]({url})" if url else f"`{sid}`")
    return " ".join(tags)


def _render_pour(issue, prices_html=""):
    """Render the Pour blockquote, wrapped in a band that also contains
    the price strip when one is supplied."""
    pour_lines = [f"> **The Pour.** {_esc(issue['pour'])}"]
    today = issue.get("today") or []
    if today:
        parts = [f"{_esc(t['teaser'])} _{_esc(t['beat'])}_" for t in today]
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
        '<div class="fng-chip" '
        'aria-label="Crypto Fear &amp; Greed Index" '
        'title="Crypto Fear &amp; Greed Index. '
        'Scale 0 (extreme fear) to 100 (extreme greed).">'
        '<span class="fng-label">Fear &amp; Greed</span>'
        f'<span class="fng-value">{today}<span class="fng-scale">/100</span></span>'
        f'<span class="fng-class">{_esc(label)}</span>'
        f'{delta_html}'
        '</div>'
    )


def _render_lead(lead, fng=None, slug=None):
    parts = ['<section class="lead" markdown="1">', ""]
    parts.append(f"**{_esc(lead.get('kicker', ''))}**")
    parts.append("{: .kicker}")
    parts.append("")
    parts.append(f"## {_esc(lead.get('headline', ''))}")
    # Stable anchor (matches lead_slug in front matter) so the lead story is
    # deep-linkable and searchable, instead of relying on kramdown's auto-id.
    if slug:
        parts.append(f"{{: #{slug}}}")
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
        parts.append(f"**{_esc(block['label'])}.** {_esc(block['text'])}")
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
        # Dimensions (cards are 1200x300) reserve space to avoid layout shift;
        # lazy/async defer these below-the-fold banners.
        parts.append(
            f'<img class="section-card" '
            f'src="{{{{ "{section_card_path}" | relative_url }}}}" '
            f'alt="{_esc_attr(title)}" width="1200" height="300" '
            f'loading="lazy" decoding="async">'
        )
        parts.append("")
    else:
        # Fallback when card generation failed — beat is never unlabelled.
        parts.append(f"## {_esc(beat.get('title', ''))}")
        parts.append("")
    for item in beat.get("items") or []:
        sources = _render_source_tags(item.get("links") or [])
        suffix = f" {sources}" if sources else ""
        parts.append(f"> **{_esc(item.get('lead_in', ''))}** {_esc(item.get('text', ''))}{suffix}")
        # Stable anchor id (precomputed in _assign_slugs) so each story is
        # deep-linkable and matches the beats: front matter.
        slug = item.get("slug")
        if slug:
            parts.append(f"{{: #{slug}}}")
        parts.append("")
    return "\n".join(parts).rstrip()


def _render_brewing(brewing):
    parts = ["## What else is grinding?", "{: .brewing-label}", ""]
    for item in brewing:
        sources = _render_source_tags(item.get("links") or [])
        suffix = f" {sources}" if sources else ""
        parts.append(f"- {_esc(item['text'])}{suffix}")
    return "\n".join(parts)


def _render_last_sip(issue):
    return (
        "---\n\n"
        f"> **Last sip.** {_esc(issue['last_sip'])}\n"
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


def _render_body(issue, prices, section_cards=None, fng=None, beats=None, lead_slug=None):
    section_cards = section_cards or {}
    prices_html = render_strip_html(prices, mode="web") if prices else ""
    blocks = []
    mood_html = _render_mood_gauge(prices)
    if mood_html:
        blocks.append(mood_html)
    blocks.append(_render_pour(issue, prices_html=prices_html))

    if issue.get("lead"):
        blocks.append(_render_lead(issue["lead"], fng=fng, slug=lead_slug))

    # Pre-slugged beats (shared with the front matter) so body anchors match.
    if beats is None:
        beats = _assign_slugs(issue.get("beats") or [])
    for beat in beats:
        blocks.append(_render_beat(beat, section_cards.get(beat.get("id"))))

    if issue.get("brewing"):
        blocks.append(_render_brewing(issue["brewing"]))

    blocks.append(_render_last_sip(issue))

    return "\n\n".join(blocks) + "\n"


def _yaml_quote(value):
    """Return a safe single-line YAML scalar for arbitrary text. Delegates all
    escaping (quotes, backslashes, newlines, control chars) to PyYAML rather
    than hand-rolling it, so model/feed values can't break out of the scalar and
    inject front-matter keys. `width` is set huge to keep it on one line."""
    dumped = yaml.safe_dump(
        {"_": str(value or "")},
        default_style='"', allow_unicode=True, width=10**9,
    )
    # dumped looks like:  "_": "<escaped value>"\n  — keep just the value scalar.
    return dumped[dumped.index(":") + 1:].strip()


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
    # One issue-wide slugger covers the lead headline first (document order),
    # then the beat items, so every anchor is unique and the body matches the
    # front matter exactly.
    slugger = _make_slugger()
    # Lead headline as its own field so layouts can use it for og:title /
    # twitter:title (the post `title` is just the dated masthead). Omitted on a
    # quiet day with no lead; layouts then fall back to the dated title.
    headline = (issue.get("lead") or {}).get("headline")
    lead_slug = slugger(headline) if headline else None
    if headline:
        fm.append(f"headline: {_yaml_quote(headline)}")
        # Stable anchor for the lead story (search + deep links read this).
        fm.append(f"lead_slug: {lead_slug}")
    if card_path:
        fm.append(f"card: {card_path}")
    # Structured story data (beat pages + search read this). Slugs computed once
    # and reused for the body anchors so the two always match.
    beats = _assign_slugs(issue.get("beats") or [], slugger)
    beats_fm = _beats_front_matter(beats)
    if beats_fm:
        fm.append(beats_fm)
    fm.append("---")
    fm.append("")
    fm.append("")
    front_matter = "\n".join(fm)

    out_path = Path(POSTS_DIR) / f"{iso}-cryptoccino.md"
    out_path.write_text(
        front_matter
        + _render_body(
            issue, prices, section_cards=section_cards, fng=fng,
            beats=beats, lead_slug=lead_slug,
        )
    )
    return str(out_path)
