"""Build news.json — a recent, deduped headline feed for the TV news rail.

Reuses pipeline.ingest.fetch_feeds (the same sources curated in feeds.yaml), so
the rail is "curated" by the same feed list as the daily brief. Run hourly by
.github/workflows/news.yml, which publishes the result to the dedicated
`news-data` branch (NOT main, so main's history and Pages builds stay clean).
The /tv/ terminal fetches it from raw.githubusercontent.com (CORS-open) and polls.

Usage: python -m pipeline.news [OUTPUT_PATH]   (default: assets/data/news.json)
"""

import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from pipeline.ingest import fetch_feeds

logger = logging.getLogger(__name__)

DEFAULT_OUT = Path("assets/data/news.json")
WINDOW_HOURS = 12   # how far back an item may be to appear in the rail
MAX_ITEMS = 40      # cap the rail


def build_news(items=None):
    """Return a list of {title, link, source, ts} dicts, newest first."""
    items = fetch_feeds() if items is None else items
    cutoff = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    seen = set()
    out = []
    for it in sorted(items, key=lambda x: x["published"], reverse=True):
        link = (it.get("link") or "").strip()
        if not link.lower().startswith(("http://", "https://")):
            continue
        if link in seen or it["published"] < cutoff:
            continue
        seen.add(link)
        out.append({
            "title": (it.get("title") or "").strip(),
            "link": link,
            "source": it.get("source_id", ""),
            "ts": int(it["published"].timestamp()),
        })
        if len(out) >= MAX_ITEMS:
            break
    return out


def main(out_path=DEFAULT_OUT):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    news = build_news()
    out_path.write_text(json.dumps(news, ensure_ascii=False, indent=1))
    print(f"Wrote {len(news)} items to {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
