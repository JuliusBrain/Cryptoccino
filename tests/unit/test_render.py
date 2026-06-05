"""Unit tests for pipeline.render."""

from pathlib import Path

from pipeline.render import (
    _format_price,
    _render_beat,
    _render_brewing,
    _render_lead,
    _render_pour,
    _render_prices,
    _render_source_tags,
    render_post,
)


class TestFormatPrice:
    def test_above_100_no_decimals_with_separator(self):
        assert _format_price(62123.45) == "62,123"

    def test_thousands(self):
        assert _format_price(60000) == "60,000"

    def test_between_1_and_100_two_decimals(self):
        assert _format_price(58.05) == "58.05"
        assert _format_price(1.10) == "1.10"

    def test_below_1_four_sig_figs(self):
        assert _format_price(0.08156) == "0.08156"
        assert _format_price(0.9998) == "0.9998"

    def test_handles_none(self):
        assert _format_price(None) == "0"


class TestRenderSourceTags:
    def test_empty(self):
        assert _render_source_tags([]) == ""
        assert _render_source_tags(None) == ""

    def test_single_link(self):
        out = _render_source_tags([
            {"source_id": "coindesk", "url": "https://e.example/a"},
        ])
        assert out == "[`coindesk`](https://e.example/a)"

    def test_multiple_links_space_separated(self):
        out = _render_source_tags([
            {"source_id": "coindesk", "url": "https://e.example/a"},
            {"source_id": "theblock", "url": "https://e.example/b"},
        ])
        assert "[`coindesk`](https://e.example/a)" in out
        assert "[`theblock`](https://e.example/b)" in out
        assert out.count(" ") == 1


class TestRenderPour:
    def test_basic_without_today(self):
        out = _render_pour({"pour": "Quiet day.", "today": []})
        assert "> **The Pour.** Quiet day." in out
        assert "{: .pour}" in out
        assert "Today." not in out

    def test_with_today_teasers(self):
        out = _render_pour({
            "pour": "Big day.",
            "today": [
                {"teaser": "thing one", "beat": "Markets"},
                {"teaser": "thing two", "beat": "Security Desk"},
            ],
        })
        assert "thing one _Markets_" in out
        assert "thing two _Security Desk_" in out
        assert " · " in out


class TestRenderPrices:
    def test_emits_chips_for_each_coin(self):
        markets_data = [
            {"symbol": "BTC", "name": "Bitcoin", "price": 60000, "change_24h": -5.0},
            {"symbol": "ETH", "name": "Ether",   "price": 1500,  "change_24h": 2.5},
        ]
        out = _render_prices(markets_data)
        assert '<section class="prices">' in out
        assert '<p class="prices-label">Prices</p>' in out
        assert out.count('<li class="chip">') == 2
        assert "BTC" in out and "60,000" in out
        assert "ETH" in out and "1,500" in out

    def test_marks_change_direction_correctly(self):
        markets_data = [
            {"symbol": "DOWN", "name": "x", "price": 100, "change_24h": -5.0},
            {"symbol": "UP",   "name": "y", "price": 100, "change_24h": 5.0},
            {"symbol": "FLAT", "name": "z", "price": 100, "change_24h": 0.0},
        ]
        out = _render_prices(markets_data)
        assert 'class="change down">−5.00%' in out
        assert 'class="change up">+5.00%' in out
        # Zero counts as up (>= 0) per the impl
        assert 'class="change up">+0.00%' in out


class TestRenderLead:
    def test_includes_all_parts(self):
        lead = {
            "kicker": "MARKETS",
            "headline": "Big news today",
            "links": [{"source_id": "coindesk", "url": "https://e.example/a"}],
            "blocks": [
                {"label": "What happened", "text": "Something."},
                {"label": "Why it matters", "text": "Because."},
            ],
        }
        out = _render_lead(lead)
        assert '<section class="lead" markdown="1">' in out
        assert "**MARKETS**" in out
        assert "{: .kicker}" in out
        assert "## Big news today" in out
        assert "{: .sources}" in out
        assert "**What happened.** Something." in out
        assert "**Why it matters.** Because." in out
        assert "</section>" in out

    def test_handles_no_links(self):
        lead = {
            "kicker": "X",
            "headline": "Y",
            "links": [],
            "blocks": [{"label": "L", "text": "T"}],
        }
        out = _render_lead(lead)
        assert "{: .sources}" not in out


class TestRenderBeat:
    def test_lists_items_as_blockquotes_with_sources(self):
        beat = {
            "id": "the_tape",
            "title": "Markets",
            "items": [
                {"lead_in": "BTC dips.", "text": "Explainer.",
                 "links": [{"source_id": "coindesk", "url": "https://e.example/a"}]},
                {"lead_in": "ETH dips.", "text": "More explainer.", "links": []},
            ],
        }
        out = _render_beat(beat)
        assert "## Markets" in out
        assert "> **BTC dips.** Explainer." in out
        assert "[`coindesk`](https://e.example/a)" in out
        assert "> **ETH dips.** More explainer." in out


class TestRenderBrewing:
    def test_uses_bullet_list_with_label_attribute(self):
        brewing = [
            {"text": "Minor thing.",
             "links": [{"source_id": "decrypt", "url": "https://e.example/a"}]},
            {"text": "Another minor thing.", "links": []},
        ]
        out = _render_brewing(brewing)
        assert "## What else is brewing" in out
        assert "{: .brewing-label}" in out
        assert "- Minor thing. [`decrypt`](https://e.example/a)" in out
        assert "- Another minor thing." in out


def _minimal_issue():
    return {
        "pour": "mood line",
        "today": [],
        "lead": None,
        "beats": [
            {"id": "the_tape", "title": "Markets",
             "items": [{"lead_in": "x", "text": "y", "links": []}]},
        ],
        "brewing": [],
        "last_sip": "quiet line",
    }


class TestRenderPost:
    def test_writes_file_with_front_matter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()

        path = render_post(_minimal_issue(), markets=[])

        assert Path(path).exists()
        content = Path(path).read_text()
        assert content.startswith("---\nlayout: issue\n")
        assert 'title: "Cryptoccino — ' in content
        assert "## Markets" in content
        assert "> **Last sip.** quiet line" in content
        assert "{: .last-sip}" in content

    def test_omits_prices_when_markets_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), markets=[])
        content = Path(path).read_text()
        assert '<section class="prices">' not in content

    def test_includes_prices_when_markets_supplied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(
            _minimal_issue(),
            markets=[
                {"symbol": "BTC", "name": "Bitcoin",
                 "price": 60000, "change_24h": -1.0},
            ],
        )
        content = Path(path).read_text()
        assert '<section class="prices">' in content
        assert "BTC" in content

    def test_omits_lead_when_null(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), markets=[])
        content = Path(path).read_text()
        assert '<section class="lead"' not in content

    def test_omits_brewing_when_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), markets=[])
        content = Path(path).read_text()
        assert "What else is brewing" not in content
