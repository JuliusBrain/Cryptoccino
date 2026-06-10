"""Render raster favicons from assets/cryptoccino-icon.png.

Browsers without SVG-favicon support (notably older Safari) ignore the SVG
favicon and fall back to a generated letter ("C"); these raster outputs give
them the coffee cup instead. Run by hand when the source icon changes — not
part of the daily pipeline:

    python scripts/generate_favicons.py

Outputs (committed):
    favicon.ico                  root, multi-size (16/32/48); browsers auto-request /favicon.ico
    assets/favicon-32x32.png
    assets/favicon-16x16.png
    assets/apple-touch-icon.png  180x180, opaque cappuccino background for iOS
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "cryptoccino-icon.png"
BG = (234, 224, 207)  # #EAE0CF — the site background; apple-touch must be opaque.


def _scaled(src, size):
    return src.resize((size, size), Image.LANCZOS)


def main():
    src = Image.open(SRC).convert("RGBA")

    _scaled(src, 32).save(ROOT / "assets" / "favicon-32x32.png")
    _scaled(src, 16).save(ROOT / "assets" / "favicon-16x16.png")

    # Multi-resolution .ico (Pillow downsizes from the source for each size).
    src.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # apple-touch-icon: opaque tile (iOS squares/rounds it and dislikes alpha).
    touch = Image.new("RGB", (180, 180), BG)
    icon = _scaled(src, 180)
    touch.paste(icon, (0, 0), icon)
    touch.save(ROOT / "assets" / "apple-touch-icon.png")

    print("Wrote favicon.ico, assets/favicon-32x32.png, "
          "assets/favicon-16x16.png, assets/apple-touch-icon.png")


if __name__ == "__main__":
    sys.exit(main())
