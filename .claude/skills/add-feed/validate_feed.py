#!/usr/bin/env python3
"""Validate that a candidate RSS/Atom feed is live and parseable before it is
added to config/feeds.yaml.

Mirrors pipeline/ingest._fetch_one: same browser User-Agent, same 15s timeout,
same feedparser.parse path — so "validates here" means "will work in the daily
run". Also checks the proposed id is not already present in feeds.yaml.

Usage:
    python validate_feed.py <url> [--id <feed_id>]

Exit 0 and print a short summary on success; exit 1 with the reason on failure.
"""

import re
import sys
from pathlib import Path

import feedparser
import requests
import yaml

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT_S = 15
FEEDS_PATH = Path("config/feeds.yaml")


def fail(msg: str) -> None:
    print(f"INVALID: {msg}")
    sys.exit(1)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        fail("usage: validate_feed.py <url> [--id <feed_id>]")

    url = args[0]
    # Only fetch http(s) feeds. Blocks file://, gopher://, etc. and keeps this
    # validator from being repurposed into an SSRF/local-file primitive if it
    # ever gets a URL from somewhere less trusted than a developer's shell.
    if not re.match(r"(?i)^https?://", url.strip()):
        fail(f"url must start with http:// or https:// (got {url!r})")

    feed_id = None
    if "--id" in args:
        i = args.index("--id")
        feed_id = args[i + 1] if i + 1 < len(args) else None

    # Duplicate-id check against the existing config.
    if feed_id and FEEDS_PATH.exists():
        config = yaml.safe_load(FEEDS_PATH.read_text()) or {}
        existing = {f.get("id") for f in (config.get("feeds") or [])}
        if feed_id in existing:
            fail(f"id '{feed_id}' already exists in {FEEDS_PATH}")

    try:
        resp = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_S
        )
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - report any fetch failure verbatim
        fail(f"fetch failed: {exc.__class__.__name__}: {exc}")

    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:
        fail(f"not parseable as a feed: {getattr(parsed, 'bozo_exception', 'unknown error')}")
    if not parsed.entries:
        fail("feed parsed but contains zero entries")

    title = (parsed.feed.get("title") or "untitled").strip()
    sample = (parsed.entries[0].get("title") or "").strip()
    print(f"VALID: '{title}' — {len(parsed.entries)} entries")
    print(f"  latest: {sample[:100]}")


if __name__ == "__main__":
    main()
