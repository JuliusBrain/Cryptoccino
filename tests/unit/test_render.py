"""Unit tests for pipeline.render."""

from pathlib import Path

from pipeline.render import (
    _assign_slugs,
    _render_beat,
    _render_brewing,
    _render_fng_chip,
    _render_last_sip,
    _render_lead,
    _render_mood_gauge,
    _render_pour,
    _render_source_tags,
    _slugify,
    render_post,
)


class TestStorySlugs:
    def test_slugify_basic(self):
        assert _slugify("Bitcoin breaks below $60,000!") == "bitcoin-breaks-below-60000"
        assert _slugify("  Spaces & symbols -- here ") == "spaces-symbols-here"
        assert _slugify("") == "story"

    def test_beat_item_gets_anchor_id(self):
        beat = {"id": "the_tape", "title": "Markets", "items": [
            {"lead_in": "Bitcoin breaks below $60k", "text": "It fell.", "links": []},
        ]}
        # Slugs are assigned once per issue; render the slugged beat (the path
        # the pipeline ships) rather than relying on a render-time fallback.
        out = _render_beat(_assign_slugs([beat])[0])
        assert "{: #bitcoin-breaks-below-60k}" in out

    def test_duplicate_lead_ins_are_deduped(self):
        beat = {"id": "the_tape", "title": "Markets", "items": [
            {"lead_in": "Same lead", "text": "a", "links": []},
            {"lead_in": "Same lead", "text": "b", "links": []},
        ]}
        out = _render_beat(_assign_slugs([beat])[0])
        assert "{: #same-lead}" in out
        assert "{: #same-lead-2}" in out

    def test_pour_and_last_sip_have_no_id(self):
        # The Pour and Last sip keep their .pour/.last-sip IALs, never an id.
        assert "{: #" not in _render_pour({"pour": "x", "today": []})
        assert "{: #" not in _render_last_sip({"last_sip": "y"})

    def test_front_matter_beats_slugs_match_body_anchors(self, tmp_path, monkeypatch):
        import re
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        issue = _minimal_issue()
        issue["beats"] = [
            {"id": "the_tape", "title": "Markets", "items": [
                {"lead_in": "Bitcoin breaks $60k", "text": "a", "links": []},
                {"lead_in": "Bitcoin breaks $60k", "text": "b", "links": []},  # dup
            ]},
            {"id": "security_desk", "title": "Security Desk", "items": [
                {"lead_in": "Zcash counterfeiting bug", "text": "c", "links": []},
            ]},
        ]
        content = Path(render_post(issue, prices=[])).read_text()
        fm_slugs = re.findall(r"slug: (\S+)", content)
        body_slugs = re.findall(r"\{: #(\S+?)\}", content)
        # Every front-matter slug appears as a body anchor (and dedupe held).
        assert fm_slugs == ["bitcoin-breaks-60k", "bitcoin-breaks-60k-2",
                            "zcash-counterfeiting-bug"]
        assert set(fm_slugs).issubset(set(body_slugs))
        assert "beats:" in content


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


class TestOutputEscaping:
    """Untrusted RSS content (relayed by the model) must not become live HTML.
    kramdown passes raw HTML through, so render.py escapes at every sink."""

    def test_drops_javascript_url_keeps_label(self):
        out = _render_source_tags([
            {"source_id": "evil", "url": "javascript:alert(document.domain)"},
        ])
        assert "javascript:" not in out
        assert out == "`evil`"  # link dropped, source label kept as plain code

    def test_drops_data_url(self):
        out = _render_source_tags([
            {"source_id": "x", "url": "data:text/html,<script>alert(1)</script>"},
        ])
        assert "data:" not in out
        assert "<script>" not in out

    def test_source_id_backtick_stripped(self):
        out = _render_source_tags([
            {"source_id": "a`](javascript:alert(1))`", "url": "https://e.example/a"},
        ])
        assert "`](javascript" not in out

    def test_pour_escapes_html(self):
        out = _render_pour({
            "pour": "<img src=x onerror=alert(1)>",
            "today": [{"teaser": "<b>x</b>", "beat": "Markets"}],
        })
        assert "<img src=x" not in out
        assert "&lt;img src=x onerror=alert(1)&gt;" in out
        assert "<b>x</b>" not in out

    def test_lead_escapes_headline_kicker_blocks(self):
        out = _render_lead({
            "kicker": "<i>MK</i>",
            "headline": "Hi <script>alert(1)</script>",
            "links": [],
            "blocks": [{"label": "What<x>", "text": "<svg onload=alert(1)>"}],
        })
        assert "<script>" not in out
        assert "<svg onload" not in out
        assert "&lt;script&gt;" in out

    def test_beat_alt_attribute_cannot_break_out(self):
        beat = {"title": '"><img src=x onerror=alert(1)>', "items": []}
        out = _render_beat(beat, section_card_path="/assets/cards/x.png")
        # the closing quote + tag must be neutralised inside alt="..."
        assert '"><img' not in out
        assert "&quot;&gt;&lt;img" in out

    def test_beat_item_text_escaped(self):
        beat = {
            "title": "Markets",
            "items": [{"lead_in": "<x>", "text": "<img src=x onerror=alert(1)>"}],
        }
        out = _render_beat(beat)
        assert "<img src=x" not in out

    def test_fng_label_escaped(self):
        out = _render_fng_chip({
            "today": 50, "today_label": "<img src=x onerror=alert(1)>", "delta": None,
        })
        assert "<img src=x" not in out
        assert "&lt;img" in out

    def test_brewing_and_last_sip_escaped(self):
        brew = _render_brewing([{"text": "<script>1</script>", "links": []}])
        assert "<script>" not in brew
        sip = _render_last_sip({"last_sip": "<script>2</script>"})
        assert "<script>" not in sip


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


class TestRenderMoodGauge:
    def _prices(self, *changes):
        # Build a minimal price list with the given 24h % changes per ticker.
        tickers = ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE"]
        return [
            {"ticker": t, "price": 1.0, "change_24h": c, "spark": []}
            for t, c in zip(tickers, changes)
        ]

    def test_empty_prices_returns_empty(self):
        assert _render_mood_gauge([]) == ""
        assert _render_mood_gauge(None) == ""

    def test_decaf_morning_at_one_percent(self):
        out = _render_mood_gauge(self._prices(0.5, -1.0, 0.8, -0.4, 0.2, -0.1))
        assert "Decaf morning" in out
        assert 'aria-valuenow="1"' in out
        assert out.count('bean-filled') == 1
        assert out.count('bean-empty') == 4

    def test_extra_bold_when_double_digit_move(self):
        out = _render_mood_gauge(self._prices(-6.6, -12.2, -7.1, -8.3, -7.3, -9.5))
        assert "Extra bold" in out
        assert 'aria-valuenow="5"' in out
        assert out.count('bean-filled') == 5
        assert out.count('bean-empty') == 0
        # Top mover highlighted in the detail.
        assert "12.2% (ETH)" in out

    def test_house_blend_in_middle_range(self):
        out = _render_mood_gauge(self._prices(-2.0, -5.0, 1.0, -1.0, 0.5, -0.1))
        assert "House blend" in out
        assert 'aria-valuenow="3"' in out

    def test_aria_meter_attributes_present(self):
        out = _render_mood_gauge(self._prices(-6.6, -12.2, 0, 0, 0, 0))
        assert 'role="meter"' in out
        assert 'aria-valuemin="1"' in out
        assert 'aria-valuemax="5"' in out
        assert 'aria-valuetext="Extra bold"' in out


class TestRenderPourBand:
    def test_pour_band_wraps_pour(self):
        out = _render_pour({"pour": "Quiet day.", "today": []})
        assert '<div class="pour-band" markdown="1">' in out
        assert "> **The Pour.** Quiet day." in out
        assert "</div>" in out

    def test_pour_band_includes_prices_html_when_supplied(self):
        out = _render_pour(
            {"pour": "x", "today": []},
            prices_html='<section class="prices">stub</section>',
        )
        assert "<section class=\"prices\">stub</section>" in out


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

    def test_includes_fng_chip_when_supplied(self):
        lead = {
            "kicker": "MARKETS",
            "headline": "h",
            "links": [],
            "blocks": [{"label": "L", "text": "T"}],
        }
        fng = {
            "today": 18,
            "today_label": "Extreme Fear",
            "delta": -22,
            "series": [],
        }
        out = _render_lead(lead, fng=fng)
        assert '<div class="fng-chip"' in out
        assert 'fng-value">18<' in out
        assert "Fear &amp; Greed" in out
        assert "/100" in out
        # Chip sits between sources and the first block.
        assert out.index("fng-chip") < out.index("**L.**")


class TestRenderFngChip:
    def test_empty_when_none(self):
        assert _render_fng_chip(None) == ""
        assert _render_fng_chip({}) == ""

    def test_extreme_fear_down_22(self):
        out = _render_fng_chip({
            "today": 18, "today_label": "Extreme Fear", "delta": -22, "series": []
        })
        assert 'fng-value">18<' in out
        assert "Extreme Fear" in out
        assert 'fng-delta down">−22 / 7d' in out

    def test_greed_up_15(self):
        out = _render_fng_chip({
            "today": 72, "today_label": "Greed", "delta": 15, "series": []
        })
        assert 'fng-value">72<' in out
        assert 'fng-delta up">+15 / 7d' in out

    def test_missing_delta_omits_delta_span(self):
        out = _render_fng_chip({
            "today": 50, "today_label": "Neutral", "delta": None, "series": []
        })
        assert "fng-delta" not in out
        assert "Neutral" in out


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
        assert "## What else is grinding?" in out
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

        path = render_post(_minimal_issue(), prices=[])

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
        path = render_post(_minimal_issue(), prices=[])
        content = Path(path).read_text()
        assert '<section class="prices">' not in content

    def test_includes_prices_when_prices_supplied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(
            _minimal_issue(),
            prices=[
                {"ticker": "BTC", "price": 60000,
                 "change_24h": -1.0, "spark": [1, 2, 3]},
            ],
        )
        content = Path(path).read_text()
        assert '<section class="prices">' in content
        assert "BTC" in content
        # Strip lives inside the Pour band wrapper.
        assert '<div class="pour-band"' in content

    def test_omits_lead_when_null(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), prices=[])
        content = Path(path).read_text()
        assert '<section class="lead"' not in content

    def test_headline_in_front_matter_from_lead(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        issue = _minimal_issue()
        issue["lead"] = {
            "kicker": "MARKETS",
            "headline": "BTC slips below $60k as jobs data lands hot.",
            "links": [],
            "blocks": [{"label": "What happened", "text": "It fell."}],
        }
        content = Path(render_post(issue, prices=[])).read_text()
        assert 'headline: "BTC slips below $60k as jobs data lands hot."' in content

    def test_headline_omitted_when_no_lead(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        content = Path(render_post(_minimal_issue(), prices=[])).read_text()
        assert "\nheadline:" not in content

    def test_omits_brewing_when_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), prices=[])
        content = Path(path).read_text()
        assert "What else is grinding?" not in content

    def test_description_in_front_matter_from_pour(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), prices=[])
        content = Path(path).read_text()
        assert 'description: "mood line"' in content

    def test_card_path_lands_in_front_matter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(
            _minimal_issue(),
            prices=[],
            card_path="/assets/cards/2026-06-05.png",
        )
        content = Path(path).read_text()
        assert "card: /assets/cards/2026-06-05.png" in content

    def test_card_field_omitted_when_no_card(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), prices=[])
        content = Path(path).read_text()
        assert "card:" not in content

    def test_section_card_replaces_beat_h2_heading(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(
            _minimal_issue(),
            prices=[],
            section_cards={"the_tape": "/assets/cards/2026-06-05-the_tape.png"},
        )
        content = Path(path).read_text()
        # Path is wrapped in a Liquid expression so Jekyll prepends baseurl.
        assert (
            '<img class="section-card" '
            'src="{{ "/assets/cards/2026-06-05-the_tape.png" | relative_url }}" '
            'alt="Markets"'
        ) in content
        # Sized + lazy-loaded to cut layout shift and defer below-fold banners.
        assert 'width="1200" height="300" loading="lazy" decoding="async">' in content
        # Banner carries the beat name; the H2 heading is dropped.
        assert "## Markets" not in content

    def test_section_card_omitted_for_beats_without_mapping(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "_posts").mkdir()
        path = render_post(_minimal_issue(), prices=[], section_cards={})
        content = Path(path).read_text()
        assert "section-card" not in content
