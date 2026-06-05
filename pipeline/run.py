"""Daily orchestrator: init_db -> ingest -> filter_new -> curate -> render -> mark_seen.

Invoked by .github/workflows/daily.yml. A day with zero new items is a quiet
skip (exit 0, no issue written). Any other failure propagates and fails the run.

Markets are fetched separately from CoinMarketCap and handed to the renderer
alongside the curated issue. A failed market fetch never breaks the run; it
just drops the price strip.
"""

import logging

from pipeline.curate import curate
from pipeline.ingest import fetch_feeds
from pipeline.markets import fetch_markets
from pipeline.render import render_post
from pipeline.store import filter_new, init_db, mark_seen

logger = logging.getLogger(__name__)


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

    logger.info("Fetching market data.")
    markets = fetch_markets()
    logger.info("Fetched %d coins for price strip.", len(markets))

    logger.info("Rendering Jekyll post.")
    path = render_post(issue, markets)
    logger.info("Wrote %s.", path)

    logger.info("Marking %d items as seen.", len(new))
    mark_seen(new)

    logger.info("Done.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
