"""Unit tests for pipeline.markets."""

import pytest
import responses

from pipeline import markets


def _coin(name, symbol, price, change):
    return {
        "name": name,
        "symbol": symbol,
        "quote": {"USD": {"price": price, "percent_change_24h": change}},
    }


CMC_RESPONSE = {
    "status": {"error_code": 0},
    "data": [
        _coin("Bitcoin",     "BTC",  60000.5, -5.0),
        _coin("Ethereum",    "ETH",  1500.0, -10.0),
        _coin("Tether",      "USDT", 1.0001, 0.01),
        _coin("BNB",         "BNB",  580.0,  -3.0),
        _coin("USDC",        "USDC", 0.9998, -0.01),
        _coin("XRP",         "XRP",  1.10,   -6.0),
        _coin("Solana",      "SOL",  65.0,   -7.0),
        _coin("TRON",        "TRX",  0.32,   -2.0),
        _coin("Hyperliquid", "HYPE", 58.0,   -14.0),
        _coin("Dogecoin",    "DOGE", 0.08,   -9.0),
        _coin("Cardano",     "ADA",  0.30,   -5.0),
        _coin("Litecoin",    "LTC",  70.0,   -3.0),
    ],
}


@pytest.fixture
def cmc_key(monkeypatch):
    monkeypatch.setenv("CMC_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def no_exclude_stables(monkeypatch):
    monkeypatch.delenv("EXCLUDE_STABLES", raising=False)


class TestFetchMarkets:
    def test_returns_empty_without_key(self, monkeypatch):
        monkeypatch.delenv("CMC_API_KEY", raising=False)
        assert markets.fetch_markets() == []

    @responses.activate
    def test_parses_cmc_response(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, json=CMC_RESPONSE)
        coins = markets.fetch_markets()
        assert len(coins) == 10
        assert coins[0] == {
            "rank": 1,
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": 60000.5,
            "change_24h": -5.0,
        }

    @responses.activate
    def test_uppercases_symbol(self, cmc_key):
        lowercase = {"status": {}, "data": [_coin("Bitcoin", "btc", 60000, -1.0)]}
        responses.add(responses.GET, markets.ENDPOINT, json=lowercase)
        coins = markets.fetch_markets()
        assert coins[0]["symbol"] == "BTC"

    @responses.activate
    def test_sends_api_key_header(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, json=CMC_RESPONSE)
        markets.fetch_markets()
        headers = responses.calls[0].request.headers
        assert headers["X-CMC_PRO_API_KEY"] == "test-key"
        assert headers["Accept"] == "application/json"

    @responses.activate
    def test_sends_expected_params(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, json=CMC_RESPONSE)
        markets.fetch_markets()
        url = responses.calls[0].request.url
        assert "convert=USD" in url
        assert "limit=10" in url
        assert "start=1" in url

    @responses.activate
    def test_excludes_stables_and_backfills(self, cmc_key, monkeypatch):
        monkeypatch.setenv("EXCLUDE_STABLES", "1")
        responses.add(responses.GET, markets.ENDPOINT, json=CMC_RESPONSE)
        coins = markets.fetch_markets()
        symbols = [c["symbol"] for c in coins]
        assert "USDT" not in symbols
        assert "USDC" not in symbols
        assert len(coins) == 10  # backfilled with ADA + LTC

    @responses.activate
    def test_excludes_stables_uses_limit_15(self, cmc_key, monkeypatch):
        monkeypatch.setenv("EXCLUDE_STABLES", "1")
        responses.add(responses.GET, markets.ENDPOINT, json=CMC_RESPONSE)
        markets.fetch_markets()
        assert "limit=15" in responses.calls[0].request.url

    @responses.activate
    def test_returns_empty_on_http_error(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, status=500)
        assert markets.fetch_markets() == []

    @responses.activate
    def test_returns_empty_on_unauthorized(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, status=401)
        assert markets.fetch_markets() == []

    @responses.activate
    def test_returns_empty_on_malformed_body(self, cmc_key):
        responses.add(responses.GET, markets.ENDPOINT, body="not json")
        assert markets.fetch_markets() == []


class TestExcludeStablesFlag:
    @pytest.mark.parametrize("value,expected", [
        ("1", True), ("true", True), ("yes", True),
        ("TRUE", True), ("Yes", True),
        ("0", False), ("false", False), ("", False), ("no", False),
    ])
    def test_truthy_values(self, monkeypatch, value, expected):
        monkeypatch.setenv("EXCLUDE_STABLES", value)
        assert markets._exclude_stables_flag() is expected
