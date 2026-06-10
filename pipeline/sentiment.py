"""Crypto Fear & Greed Index from alternative.me.

One request per daily run. The value is passed into the curate call so
the model can reference it in a lead block when it strengthens the
narrative, and is also rendered as a small chip near the lead headline
so the data point is visible even if the model didn't lean on it.

Fail-open: any HTTP / parse failure falls back to the JSON cache at
assets/data/fng.json. With no usable cache the function returns None
and the issue builds without a sentiment data point.
"""

import json
import logging
from pathlib import Path

import requests

from pipeline.cache import read_json, write_json

logger = logging.getLogger(__name__)

ENDPOINT = "https://api.alternative.me/fng/"
REQUEST_TIMEOUT_S = 10
CACHE_PATH = Path("assets/data/fng.json")
WINDOW_DAYS = 8  # today + 7 days back


def fetch_fng():
    """Return {today, today_label, week_ago, delta, series} or None.

    series is a list of ints ordered oldest -> today. delta is the
    seven-day change in the index value (today - week_ago).
    """
    try:
        response = requests.get(
            ENDPOINT, params={"limit": WINDOW_DAYS}, timeout=REQUEST_TIMEOUT_S
        )
        response.raise_for_status()
        raw = response.json().get("data") or []
    except Exception as exc:
        logger.warning(
            "F&G fetch failed: %s: %s. Falling back to cache.",
            exc.__class__.__name__, exc,
        )
        return read_json(CACHE_PATH)

    if not raw:
        return read_json(CACHE_PATH)

    # API returns newest first; reverse to oldest -> today.
    by_age = list(reversed(raw))
    series = [int(d["value"]) for d in by_age]
    today_entry = raw[0]
    today = int(today_entry["value"])
    today_label = today_entry.get("value_classification", "")
    # Use the oldest available entry as the ~7-day baseline. alternative.me
    # sometimes returns limit-1 (a missing day); tolerate that instead of
    # dropping the delta entirely. Give up only if the series is too short.
    week_ago = int(raw[-1]["value"]) if len(raw) >= WINDOW_DAYS - 1 else None
    delta = today - week_ago if week_ago is not None else None

    result = {
        "today": today,
        "today_label": today_label,
        "week_ago": week_ago,
        "delta": delta,
        "series": series,
    }
    write_json(CACHE_PATH, result)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    print(json.dumps(fetch_fng(), indent=2))
