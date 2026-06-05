"""Daily orchestrator: init_db -> ingest -> filter_new -> curate -> render -> mark_seen.

Invoked by .github/workflows/daily.yml. A day with zero new items is a quiet
skip (exit 0, no issue written). Any other failure propagates and fails the run.
"""

import logging

from pipeline.curate import curate
from pipeline.ingest import fetch_feeds
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
    stories = sum(len(b.get("stories", [])) for b in beats)
    logger.info("Curated %d beats with %d stories total.", len(beats), stories)

    logger.info("Rendering Jekyll post.")
    path = render_post(issue)
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
