"""Unit tests for pipeline.prices."""

import json
from unittest.mock import patch

import pytest
import responses

from pipeline import prices
from pipeline.prices import (
    _downsample,
    _svg_sparkline,
    fetch_prices,
    format_change,
    format_price,
    render_strip_html,
)


# --------------------------------------------------------------------------
# Fixtures: a minimal CoinGecko-shaped response covering all 6 coins.
# --------------------------------------------------------------------------

def _coin(coin_id, price, change, n_spark=168):
    return {
        "id": coin_id,
        "current_price": price,
        "price_change_percentage_24h": change,
        "sparkline_in_7d": {"price": [price * (1 + i * 0.001) for i in range(n_spark)]},
    }


CG_RESPONSE = [
    _coin("bitcoin", 60000.0, -5.0),
    _coin("ethereum", 1500.0, -10.0),
    _coin("binancecoin", 580.0, -3.0),
    _coin("solana", 65.0, -7.0),
    _coin("ripple", 1.10, -6.0),
    _coin("dogecoin", 0.08, -9.0),
]


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    cache = tmp_path / "data" / "prices.json"
    monkeypatch.setattr(prices, "CACHE_PATH", cache)
    monkeypatch.setattr(prices, "SPARKLINES_DIR", tmp_path / "sparklines")
    return cache


@pytest.fixture
def no_demo_key(monkeypatch):
    monkeypatch.delenv("COINGECKO_KEY", raising=False)


# --------------------------------------------------------------------------
# fetch_prices
# --------------------------------------------------------------------------

class TestFetchPrices:
    @responses.activate
    def test_parses_response_and_caches(
        self, isolated_cache, no_demo_key
    ):
        responses.add(responses.GET, prices.ENDPOINT, json=CG_RESPONSE)
        result = fetch_prices()
        assert len(result) == 6
        first = result[0]
        assert first["ticker"] == "BTC"
        assert first["price"] == 60000.0
        assert first["change_24h"] == -5.0
        # Downsampled to ~30.
        assert len(first["spark"]) == 30
        # Cache file written.
        assert isolated_cache.exists()
        cached = json.loads(isolated_cache.read_text())
        assert cached[0]["ticker"] == "BTC"

    @responses.activate
    def test_preserves_canonical_order(self, isolated_cache, no_demo_key):
        # Shuffle the API response; result must still be in BTC, ETH, BNB,
        # SOL, XRP, DOGE order.
        shuffled = [CG_RESPONSE[5], CG_RESPONSE[0], CG_RESPONSE[3],
                    CG_RESPONSE[2], CG_RESPONSE[4], CG_RESPONSE[1]]
        responses.add(responses.GET, prices.ENDPOINT, json=shuffled)
        result = fetch_prices()
        tickers = [p["ticker"] for p in result]
        assert tickers == ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE"]

    @responses.activate
    def test_sends_demo_key_when_env_set(
        self, isolated_cache, monkeypatch
    ):
        monkeypatch.setenv("COINGECKO_KEY", "demo-key")
        responses.add(responses.GET, prices.ENDPOINT, json=CG_RESPONSE)
        fetch_prices()
        assert (
            responses.calls[0].request.headers["x-cg-demo-api-key"]
            == "demo-key"
        )

    @responses.activate
    def test_falls_back_to_cache_on_http_error(
        self, isolated_cache, no_demo_key
    ):
        # Seed a cache.
        isolated_cache.parent.mkdir(parents=True, exist_ok=True)
        seeded = [{"ticker": "BTC", "price": 1, "change_24h": 0, "spark": [1, 2, 3]}]
        isolated_cache.write_text(json.dumps(seeded))

        responses.add(responses.GET, prices.ENDPOINT, status=500)
        result = fetch_prices()
        assert result == seeded

    @responses.activate
    def test_returns_none_when_no_cache_and_fetch_fails(
        self, isolated_cache, no_demo_key
    ):
        responses.add(responses.GET, prices.ENDPOINT, status=500)
        assert fetch_prices() is None

    @responses.activate
    def test_returns_none_on_empty_response_with_no_cache(
        self, isolated_cache, no_demo_key
    ):
        responses.add(responses.GET, prices.ENDPOINT, json=[])
        assert fetch_prices() is None


# --------------------------------------------------------------------------
# downsample
# --------------------------------------------------------------------------

class TestDownsample:
    def test_returns_empty_when_no_points(self):
        assert _downsample([], 30) == []

    def test_returns_as_is_when_already_small(self):
        pts = [1.0, 2.0, 3.0]
        assert _downsample(pts, 30) == pts

    def test_downsamples_to_target(self):
        pts = list(range(168))
        out = _downsample(pts, 30)
        assert len(out) == 30
        assert out[0] == 0
        assert out[-1] < 168


# --------------------------------------------------------------------------
# formatters
# --------------------------------------------------------------------------

class TestFormatPrice:
    def test_above_100_no_decimals(self):
        assert format_price(62123.45) == "$62,123"
        assert format_price(60000) == "$60,000"

    def test_between_1_and_100_two_decimals(self):
        assert format_price(58.05) == "$58.05"
        assert format_price(1.10) == "$1.10"

    def test_below_1_four_decimals(self):
        assert format_price(0.142) == "$0.1420"
        assert format_price(0.08156) == "$0.0816"

    def test_none(self):
        assert format_price(None) == "$0"


class TestFormatChange:
    def test_positive_plus_sign(self):
        assert format_change(2.34) == "+2.3%"

    def test_zero_plus_sign(self):
        assert format_change(0) == "+0.0%"

    def test_negative_minus_sign(self):
        # The Unicode minus sign, not the ASCII hyphen-minus.
        assert format_change(-2.34) == "−2.3%"


# --------------------------------------------------------------------------
# Sparkline renderers
# --------------------------------------------------------------------------

class TestSvgSparkline:
    def test_empty(self):
        assert _svg_sparkline([]) == ""
        assert _svg_sparkline([1.0]) == ""

    def test_up_colors_green(self):
        out = _svg_sparkline([1.0, 2.0, 3.0])
        assert prices.UP in out

    def test_down_colors_red(self):
        out = _svg_sparkline([3.0, 2.0, 1.0])
        assert prices.DOWN in out

    def test_dot_at_last_point(self):
        out = _svg_sparkline([1.0, 2.0, 3.0])
        assert "<circle" in out


# --------------------------------------------------------------------------
# render_strip_html
# --------------------------------------------------------------------------

SAMPLE_PRICES = [
    {"ticker": "BTC", "price": 60000, "change_24h": 1.2, "spark": [1, 2, 3]},
    {"ticker": "ETH", "price": 1500, "change_24h": -3.4, "spark": [3, 2, 1]},
]


class TestRenderStripHtml:
    def test_empty_returns_empty_string(self):
        assert render_strip_html([]) == ""
        assert render_strip_html(None) == ""

    def test_web_mode_emits_chips_with_svg(self):
        out = render_strip_html(SAMPLE_PRICES, mode="web")
        assert '<section class="prices">' in out
        assert out.count('<li class="chip">') == 2
        assert "BTC" in out and "$60,000" in out
        assert "ETH" in out and "$1,500" in out
        assert "<svg" in out
        assert 'class="change up">+1.2%' in out
        assert 'class="change down">−3.4%' in out

    def test_email_mode_emits_img_tag(self, isolated_cache):
        # email mode writes PNGs via matplotlib + references them by path.
        out = render_strip_html(SAMPLE_PRICES, mode="email")
        assert "<svg" not in out
        assert '<img class="spark"' in out
        # Both ticker images written.
        assert (prices.SPARKLINES_DIR / "BTC.png").exists()
        assert (prices.SPARKLINES_DIR / "ETH.png").exists()
