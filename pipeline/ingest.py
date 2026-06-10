"""Fetch RSS feeds listed in config/feeds.yaml and return normalised items.

Each feed is fetched in isolation with a 15s timeout and a browser User-Agent
(several sources reject the default UA or curl-like clients). Per-feed errors
are logged and swallowed so a single dead source never aborts the daily run.
"""

import html
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
import yaml

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_S = 15
# Feeds are independent network I/O, so fetch them concurrently. Capped so a
# large feed list can't open an unbounded number of sockets at once.
MAX_FETCH_WORKERS = 8


def _strip_html(value):
    if not value:
        return ""
    no_tags = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(no_tags)).strip()


def _parse_published(entry):
    for key in ("published_parsed", "updated_parsed"):
        struct_time = entry.get(key)
        if struct_time:
            return datetime(*struct_time[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _fetch_one(feed_cfg):
    response = requests.get(
        feed_cfg["url"],
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_S,
    )
    response.raise_for_status()
    parsed = feedparser.parse(response.content)

    items = []
    for entry in parsed.entries:
        items.append({
            "source_id": feed_cfg["id"],
            "category": feed_cfg["category"],
            "title": (entry.get("title") or "").strip(),
            "link": (entry.get("link") or "").strip(),
            "summary": _strip_html(entry.get("summary") or entry.get("description") or ""),
            "published": _parse_published(entry),
        })
    return items


def _fetch_one_safe(feed_cfg):
    """Fetch a single feed, returning its items or [] on any error.

    Per-feed isolation lives here so each concurrent worker swallows its own
    failure — one dead source never aborts the run or another worker.
    """
    feed_id = feed_cfg["id"]
    try:
        items = _fetch_one(feed_cfg)
    except Exception as exc:
        logger.warning("%s failed: %s: %s", feed_id, exc.__class__.__name__, exc)
        print(f"  {feed_id}: skipped")
        return []
    print(f"  {feed_id}: {len(items)} items")
    return items


def fetch_feeds(config_path="config/feeds.yaml"):
    """Load feeds.yaml and pull every configured feed concurrently, returning
    normalised items. Worst-case wall time drops from the sum of per-feed
    latencies to roughly the single slowest feed."""
    config = yaml.safe_load(Path(config_path).read_text())
    feeds = config["feeds"]
    all_items = []
    with ThreadPoolExecutor(max_workers=MAX_FETCH_WORKERS) as pool:
        for items in pool.map(_fetch_one_safe, feeds):
            all_items.extend(items)
    return all_items


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    print("Fetching feeds...")
    items = fetch_feeds()
    print(f"\nTotal: {len(items)} items across all feeds.")
