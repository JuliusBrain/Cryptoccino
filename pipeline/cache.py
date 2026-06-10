"""Shared fail-open JSON cache read/write for the price strip and sentiment.

Both helpers swallow every error and log a warning: a missing or corrupt cache
is a degrade-gracefully condition (fall back / continue without the data point),
never a run-aborting one.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_json(path):
    """Return the parsed JSON at `path`, or None if it is missing/unreadable."""
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        logger.warning("No usable cache at %s: %s", path, exc)
        return None


def write_json(path, data):
    """Write `data` as indented JSON to `path`, creating parents. Swallows errors."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
    except Exception as exc:
        logger.warning("Could not write cache at %s: %s", path, exc)
