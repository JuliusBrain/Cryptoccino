"""Generate branded social cards (1200x630 PNG) for daily issues.

Pillow-only at runtime. The icon is composited from the pre-rendered
PNG at assets/cryptoccino-icon.png so no SVG library is needed in
production. Fonts are loaded by path from assets/fonts/ — no system
font dependency, so CI works the same as a developer's machine.

Fail-open contract: generate_card swallows every exception, logs a
warning, and returns None. The daily run then continues with no card
rather than aborting the issue.
"""

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Card dimensions (standard OG / Twitter summary_large_image).
W, H = 1200, 630
PADDING = 80
BORDER_INSET = 40

ASSETS_DIR = Path("assets")
FONTS_DIR = ASSETS_DIR / "fonts"
ICON_PATH = ASSETS_DIR / "cryptoccino-icon.png"

SERIF_REGULAR = FONTS_DIR / "PTSerif-Regular.ttf"
SERIF_BOLD = FONTS_DIR / "PTSerif-Bold.ttf"
MONO_REGULAR = FONTS_DIR / "JetBrainsMono-Regular.ttf"

# Cappuccino palette (mirrors assets/style.css :root).
BG = "#EAE0CF"
LINE = "#DECBAF"
INK = "#2E2117"
SOFT = "#4F4031"
MUT = "#7D6C58"
FAINT = "#9A8A74"
CREMA = "#A35E1E"
CREMA_DECO = "#C2823C"

# Section card (per-beat banner) dimensions.
SECTION_W, SECTION_H = 1200, 300
SECTION_BORDER_INSET = 20

SITE_DOMAIN = "cryptoccino.xyz"


def generate_card(lead, pour, date, out_path):
    """Build a 1200x630 PNG card. Return out_path on success, None on any failure."""
    try:
        return _generate_card(lead, pour, date, out_path)
    except Exception as exc:
        logger.warning("Card generation failed: %s: %s", exc.__class__.__name__, exc)
        return None


def _generate_card(lead, pour, date, out_path):
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    # Inner border.
    draw.rectangle(
        (BORDER_INSET, BORDER_INSET, W - BORDER_INSET, H - BORDER_INSET),
        outline=LINE,
        width=1,
    )

    _draw_lockup(canvas, draw)

    if lead and lead.get("headline"):
        beat_label = (lead.get("kicker") or "TODAY").upper()
        headline = lead["headline"]
    else:
        beat_label = "TODAY"
        headline = pour or ""

    _draw_meta_row(draw, beat_label, date)
    _draw_headline(draw, headline)
    _draw_footer(draw)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    return str(out_path)


def _draw_lockup(canvas, draw):
    icon = Image.open(ICON_PATH).convert("RGBA")
    icon_h = 76
    icon_w = int(icon.width * icon_h / icon.height)
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)
    canvas.paste(icon, (PADDING, PADDING), icon)

    wordmark_font = ImageFont.truetype(str(SERIF_BOLD), 40)
    wordmark_x = PADDING + icon_w + 18
    wordmark_y = PADDING + 4
    draw.text((wordmark_x, wordmark_y), "Cryptoccino", fill=INK, font=wordmark_font)

    tagline_font = ImageFont.truetype(str(MONO_REGULAR), 15)
    tagline_y = wordmark_y + 50
    draw.text(
        (wordmark_x, tagline_y),
        "YOUR DAILY SHOT OF CRYPTO",
        fill=CREMA,
        font=tagline_font,
    )


def _draw_meta_row(draw, beat_label, date):
    rule_y = 285
    draw.rectangle((PADDING, rule_y, PADDING + 90, rule_y + 6), fill=CREMA_DECO)

    meta_font = ImageFont.truetype(str(MONO_REGULAR), 16)
    meta_y = rule_y + 22
    draw.text((PADDING, meta_y), beat_label, fill=CREMA, font=meta_font)

    date_str = date.strftime("%d %B %Y").upper()
    date_bbox = draw.textbbox((0, 0), date_str, font=meta_font)
    date_w = date_bbox[2] - date_bbox[0]
    draw.text((W - PADDING - date_w, meta_y), date_str, fill=MUT, font=meta_font)


def _draw_headline(draw, headline):
    max_w = W - 2 * PADDING
    font, lines = _fit_headline(draw, headline, max_w)
    line_h = int(font.size * 1.15)
    start_y = 348
    for i, line in enumerate(lines):
        draw.text((PADDING, start_y + i * line_h), line, fill=INK, font=font)


def _draw_footer(draw):
    font = ImageFont.truetype(str(MONO_REGULAR), 14)
    y = H - BORDER_INSET - 28
    draw.text((PADDING, y), "BREWED DAILY", fill=FAINT, font=font)
    domain_bbox = draw.textbbox((0, 0), SITE_DOMAIN, font=font)
    domain_w = domain_bbox[2] - domain_bbox[0]
    draw.text((W - PADDING - domain_w, y), SITE_DOMAIN, fill=FAINT, font=font)


def _fit_headline(draw, text, max_w, max_lines=3, start_size=64, min_size=28, step=4):
    """Auto-shrink the serif until the wrapped headline fits max_lines."""
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(str(SERIF_BOLD), size)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= step
    # Even at min_size it overflows — truncate the line count.
    font = ImageFont.truetype(str(SERIF_BOLD), min_size)
    lines = _wrap(draw, text, font, max_w)[:max_lines]
    return font, lines


def _wrap(draw, text, font, max_w):
    """Greedy word-wrap with textbbox-measured fitting."""
    words = (text or "").split()
    if not words:
        return []
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        w = draw.textbbox((0, 0), trial, font=font)[2]
        if w <= max_w:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def generate_section_card(beat_title, beat_note, date, out_path):
    """Build a 1200x300 PNG section banner. Return out_path or None on failure.

    Used as a per-beat divider inside the issue body. Smaller than the hero
    card and not used as og:image. Crema rule, beat title in serif bold,
    beat note in serif regular below, date top-right in mono.
    """
    try:
        return _generate_section_card(beat_title, beat_note, date, out_path)
    except Exception as exc:
        logger.warning(
            "Section card generation failed: %s: %s", exc.__class__.__name__, exc
        )
        return None


def _generate_section_card(beat_title, beat_note, date, out_path):
    canvas = Image.new("RGB", (SECTION_W, SECTION_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Inner border.
    draw.rectangle(
        (
            SECTION_BORDER_INSET,
            SECTION_BORDER_INSET,
            SECTION_W - SECTION_BORDER_INSET,
            SECTION_H - SECTION_BORDER_INSET,
        ),
        outline=LINE,
        width=1,
    )

    # Date top-right.
    date_font = ImageFont.truetype(str(MONO_REGULAR), 14)
    date_str = date.strftime("%d %B %Y").upper()
    date_bbox = draw.textbbox((0, 0), date_str, font=date_font)
    draw.text(
        (SECTION_W - PADDING - (date_bbox[2] - date_bbox[0]), 60),
        date_str,
        fill=MUT,
        font=date_font,
    )

    # Crema rule.
    rule_y = 105
    draw.rectangle((PADDING, rule_y, PADDING + 60, rule_y + 6), fill=CREMA_DECO)

    # Beat title.
    title_font = ImageFont.truetype(str(SERIF_BOLD), 56)
    title_y = rule_y + 22
    draw.text((PADDING, title_y), beat_title, fill=INK, font=title_font)

    # Beat note (sub-tagline).
    if beat_note:
        note_font = ImageFont.truetype(str(SERIF_REGULAR), 22)
        note_y = title_y + 80
        draw.text((PADDING, note_y), beat_note, fill=SOFT, font=note_font)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)
    return str(out_path)
