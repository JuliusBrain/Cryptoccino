"""SQLite-backed seen-state for cross-day URL deduplication.

The seen table is keyed by a SHA-1 hash of the item link and records the
date the URL was first stored. filter_new drops anything already present;
mark_seen records the rest. Same-day cross-source clustering of duplicate
stories is delegated to Claude during curation, not handled here.
"""

import hashlib
import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = "data/cryptoccino.db"


def _hash(link):
    return hashlib.sha1(link.encode("utf-8")).hexdigest()


def init_db():
    """Create the SQLite database and seen table if they don't already exist."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            "url_hash TEXT PRIMARY KEY, "
            "link TEXT, "
            "source_id TEXT, "
            "first_seen TEXT"
            ")"
        )


def filter_new(items):
    """Return only items whose link hash is not already present in the seen table."""
    if not items:
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT url_hash FROM seen").fetchall()
    known = {row[0] for row in rows}
    return [item for item in items if _hash(item["link"]) not in known]


def mark_seen(items):
    """Insert items into the seen table, stamping today's date for new rows."""
    if not items:
        return
    today = date.today().isoformat()
    rows = [
        (_hash(item["link"]), item["link"], item["source_id"], today)
        for item in items
    ]
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen (url_hash, link, source_id, first_seen) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )


if __name__ == "__main__":
    from pipeline.ingest import fetch_feeds

    init_db()
    items = fetch_feeds()
    new = filter_new(items)
    print(f"\n{len(new)} of {len(items)} items are new (not in {DB_PATH}).")
