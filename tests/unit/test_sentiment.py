"""Unit tests for pipeline.sentiment."""

import json

import pytest
import responses

from pipeline import sentiment


def _api_payload(values_oldest_first):
    """Build a fake alternative.me response (newest first)."""
    values = list(reversed(values_oldest_first))
    return {
        "data": [
            {
                "value": str(v),
                "value_classification": "Extreme Fear" if v < 25 else "Fear",
                "timestamp": str(1748908800 - i * 86400),
            }
            for i, v in enumerate(values)
        ],
    }


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    cache = tmp_path / "data" / "fng.json"
    monkeypatch.setattr(sentiment, "CACHE_PATH", cache)
    return cache


class TestFetchFng:
    @responses.activate
    def test_parses_and_caches(self, isolated_cache):
        responses.add(
            responses.GET,
            sentiment.ENDPOINT,
            json=_api_payload([40, 35, 30, 28, 25, 20, 18, 18]),
        )
        result = sentiment.fetch_fng()
        assert result["today"] == 18
        assert result["today_label"] == "Extreme Fear"
        assert result["week_ago"] == 40
        assert result["delta"] == -22
        assert result["series"] == [40, 35, 30, 28, 25, 20, 18, 18]
        # Cache written.
        cached = json.loads(isolated_cache.read_text())
        assert cached["today"] == 18

    @responses.activate
    def test_falls_back_to_cache_on_http_error(self, isolated_cache):
        isolated_cache.parent.mkdir(parents=True, exist_ok=True)
        seeded = {
            "today": 50, "today_label": "Neutral",
            "week_ago": 55, "delta": -5, "series": [55] * 8,
        }
        isolated_cache.write_text(json.dumps(seeded))
        responses.add(responses.GET, sentiment.ENDPOINT, status=500)
        assert sentiment.fetch_fng() == seeded

    @responses.activate
    def test_returns_none_when_no_cache_and_fetch_fails(self, isolated_cache):
        responses.add(responses.GET, sentiment.ENDPOINT, status=500)
        assert sentiment.fetch_fng() is None

    @responses.activate
    def test_returns_none_on_empty_payload(self, isolated_cache):
        responses.add(responses.GET, sentiment.ENDPOINT, json={"data": []})
        assert sentiment.fetch_fng() is None
