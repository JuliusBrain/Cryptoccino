"""Unit tests for pipeline.market_context."""

from pipeline import market_context as mc

PRICES = [
    {"ticker": "BTC", "price": 62000, "change_24h": -2.1, "spark": []},
    {"ticker": "ETH", "price": 3400, "change_24h": -1.4, "spark": []},
]
FNG = {"today": 9, "today_label": "Extreme Fear", "delta": -5}
GLOB = {"dominance": 58.3, "mcap": 2.3e12, "volume": 95e9}


class TestBuildPrompt:
    def test_includes_key_figures(self):
        p = mc._build_prompt(PRICES, FNG, GLOB)
        assert "BTC: $62,000 (-2.1% 24h)" in p
        assert "Fear & Greed: 9 (Extreme Fear)" in p
        assert "BTC dominance: 58.3%" in p
        assert "24h total volume: $95B" in p

    def test_tolerates_missing_data(self):
        p = mc._build_prompt(PRICES, None, {})
        assert "BTC:" in p
        assert "Fear & Greed" not in p


class TestBuildContext:
    def _stub_data(self, monkeypatch, prices=PRICES, fng=FNG, glob=GLOB):
        monkeypatch.setattr(mc, "fetch_prices", lambda: prices)
        monkeypatch.setattr(mc, "fetch_fng", lambda: fng)
        monkeypatch.setattr(mc, "_fetch_global", lambda: glob)

    def test_success_shape(self, monkeypatch):
        self._stub_data(monkeypatch)
        monkeypatch.setattr(mc, "_ask_claude", lambda msg: "  Risk-off mood today.  ")
        out = mc.build_context()
        assert out["text"] == "  Risk-off mood today.  "  # _ask_claude already strips
        assert isinstance(out["ts"], int)
        assert "generated" in out

    def test_fail_open_returns_cache(self, monkeypatch):
        self._stub_data(monkeypatch)

        def boom(_msg):
            raise RuntimeError("api down")

        monkeypatch.setattr(mc, "_ask_claude", boom)
        monkeypatch.setattr(mc, "read_json", lambda path: {"text": "cached blurb", "ts": 1})
        assert mc.build_context() == {"text": "cached blurb", "ts": 1}

    def test_no_data_skips_claude_and_keeps_cache(self, monkeypatch):
        self._stub_data(monkeypatch, prices=None, fng=None, glob={})
        calls = []
        monkeypatch.setattr(mc, "_ask_claude", lambda msg: calls.append(1) or "x")
        monkeypatch.setattr(mc, "read_json", lambda path: {"text": "old"})
        out = mc.build_context()
        assert out == {"text": "old"}
        assert calls == []  # no data → no (paid) model call
