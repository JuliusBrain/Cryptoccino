"""Render the static brand share card (assets/cryptoccino-og.png).

Run by hand whenever the brand card's copy or styling changes — NOT part of the
daily pipeline. The output is committed and served as the default og:image for
the homepage and other non-issue pages.

    python scripts/generate_og_card.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.cards import generate_brand_card

OUT_PATH = "assets/cryptoccino-og.png"


if __name__ == "__main__":
    result = generate_brand_card(OUT_PATH)
    if result:
        print(f"Wrote {result}")
    else:
        raise SystemExit("Brand card generation failed; see warning above.")
