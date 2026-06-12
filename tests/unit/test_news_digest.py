"""Unit tests for pipeline.news_digest."""

from pipeline import news_digest as nd

ITEMS = [
    {"title": "BTC slips below $60k", "link": "https://a.test/1", "source": "coindesk", "ts": 3},
    {"title": "Acme raises $40M Series B", "link": "https://b.test/2", "source": "theblock", "ts": 2},
    {"title": "Bridge drained for $12M", "link": "https://c.test/3", "source": "rekt", "ts": 1},
]


class TestPrompt:
    def test_numbers_and_sources(self):
        p = nd._prompt(ITEMS)
        assert "1. [coindesk] BTC slips below $60k" in p
        assert "2. [theblock] Acme raises $40M Series B" in p
        assert "3. [rekt] Bridge drained for $12M" in p


class TestBuildDigest:
    def test_index_mapping_uses_real_link_and_source(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: list(ITEMS))
        monkeypatch.setattr(nd, "_ask_claude", lambda msg: {
            "market": [{"i": 1, "take": "majors cool off"}],
            "business": [{"i": 2, "take": "fresh raise lands"}],
            "security": [{"i": 3, "take": "another bridge falls"}],
            "policy": [],
        })
        out = nd.build_digest()
        assert out["market"] == [{
            "headline": "BTC slips below $60k",
            "take": "majors cool off",
            "source": "coindesk",
            "link": "https://a.test/1",
        }]
        assert out["security"][0]["link"] == "https://c.test/3"
        assert out["policy"] == []
        assert isinstance(out["ts"], int)
        assert "generated" in out

    def test_out_of_range_index_dropped(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: list(ITEMS))
        monkeypatch.setattr(nd, "_ask_claude", lambda msg: {
            "market": [{"i": 99, "take": "hallucinated"}, {"i": 1, "take": "real"}],
            "business": [], "security": [], "policy": [],
        })
        out = nd.build_digest()
        assert [e["take"] for e in out["market"]] == ["real"]

    def test_caps_per_category(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: list(ITEMS))
        monkeypatch.setattr(nd, "_ask_claude", lambda msg: {
            "market": [{"i": 1, "take": f"t{n}"} for n in range(10)],
            "business": [], "security": [], "policy": [],
        })
        out = nd.build_digest()
        assert len(out["market"]) == nd.MAX_PER_CATEGORY

    def test_no_candidates_skips_claude_and_keeps_cache(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: [])
        calls = []
        monkeypatch.setattr(nd, "_ask_claude", lambda msg: calls.append(1) or {})
        monkeypatch.setattr(nd, "read_json", lambda path: {"market": ["old"]})
        out = nd.build_digest()
        assert out == {"market": ["old"]}
        assert calls == []  # no candidates → no (paid) model call

    def test_fail_open_returns_cache(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: list(ITEMS))

        def boom(_msg):
            raise RuntimeError("api down")

        monkeypatch.setattr(nd, "_ask_claude", boom)
        monkeypatch.setattr(nd, "read_json", lambda path: {"cached": True})
        assert nd.build_digest() == {"cached": True}

    def test_empty_result_keeps_cache(self, monkeypatch):
        monkeypatch.setattr(nd, "build_news", lambda: list(ITEMS))
        monkeypatch.setattr(nd, "_ask_claude", lambda msg: {
            "market": [], "business": [], "security": [], "policy": [],
        })
        monkeypatch.setattr(nd, "read_json", lambda path: {"cached": "kept"})
        assert nd.build_digest() == {"cached": "kept"}
