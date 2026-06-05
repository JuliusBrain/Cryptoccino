"""Daily orchestrator: init_db -> ingest -> filter_new -> curate -> render -> mark_seen.

Invoked by .github/workflows/daily.yml. A day with zero new items is a quiet
skip (exit 0, no issue written). Any other failure propagates and fails the run.

Markets are fetched separately from CoinMarketCap and handed to the renderer
alongside the curated issue. A failed market fetch never breaks the run; it
just drops the price strip. Card generation is similarly fail-open: if the
Pillow render or asset load fails, the issue still publishes with no hero card.
"""

import logging
import shutil
from datetime import date
from pathlib import Path

import yaml

from pipeline.cards import generate_card, generate_section_card
from pipeline.curate import curate
from pipeline.ingest import fetch_feeds
from pipeline.prices import fetch_prices
from pipeline.render import render_post
from pipeline.store import filter_new, init_db, mark_seen

logger = logging.getLogger(__name__)

CARDS_DIR = Path("assets/cards")
FEEDS_CONFIG = Path("config/feeds.yaml")


def main():
    """Run one full daily cycle and write today's Jekyll post."""
    logger.info("Initialising seen-state DB.")
    init_db()

    logger.info("Fetching feeds.")
    items = fetch_feeds()
    logger.info("Fetched %d items across all feeds.", len(items))

    new = filter_new(items)
    logger.info("Filtered to %d new items.", len(new))

    if not new:
        logger.info("Nothing new today, skipping issue.")
        return

    logger.info("Curating issue with Claude.")
    issue = curate(new)
    beats = issue.get("beats", [])
    items_total = sum(len(b.get("items", [])) for b in beats)
    logger.info(
        "Curated lead=%s, %d beats with %d items, %d brewing.",
        "yes" if issue.get("lead") else "no",
        len(beats),
        items_total,
        len(issue.get("brewing") or []),
    )

    logger.info("Fetching price strip data.")
    prices = fetch_prices()
    logger.info("Fetched prices for %d coins.", len(prices) if prices else 0)

    today = date.today()
    card_relative = _generate_card_for(issue, today)
    section_cards = _generate_section_cards_for(issue, today)

    logger.info("Rendering Jekyll post.")
    path = render_post(
        issue, prices=prices, card_path=card_relative, section_cards=section_cards
    )
    logger.info("Wrote %s.", path)

    logger.info("Marking %d items as seen.", len(new))
    mark_seen(new)

    logger.info("Done.")


def _generate_card_for(issue, today):
    """Try to build today's social card. Return site-relative path or None."""
    out_path = CARDS_DIR / f"{today.isoformat()}.png"
    logger.info("Generating social card -> %s.", out_path)
    result = generate_card(issue.get("lead"), issue.get("pour"), today, str(out_path))
    if not result:
        logger.warning("Card generation returned no path; continuing without a card.")
        return None
    latest = CARDS_DIR / "latest.png"
    shutil.copyfile(result, latest)
    logger.info("Card saved and copied to %s.", latest)
    return "/" + out_path.as_posix()


def _generate_section_cards_for(issue, today):
    """Generate one card per beat. Return dict of beat_id -> site-relative path."""
    try:
        config = yaml.safe_load(FEEDS_CONFIG.read_text())
        beat_meta = config.get("beats") or {}
    except Exception as exc:
        logger.warning("Could not load feeds.yaml beats: %s", exc)
        beat_meta = {}

    result = {}
    for beat in issue.get("beats") or []:
        beat_id = beat.get("id")
        if not beat_id:
            continue
        out_path = CARDS_DIR / f"{today.isoformat()}-{beat_id}.png"
        note = (beat_meta.get(beat_id) or {}).get("note", "")
        success = generate_section_card(
            beat.get("title", ""), note, today, str(out_path)
        )
        if success:
            result[beat_id] = "/" + out_path.as_posix()
    logger.info("Generated %d section cards.", len(result))
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
