"""Unit tests for pipeline.weekly."""

from datetime import date

from pipeline import weekly as wk

STORIES = [
    {"date": date(2026, 6, 15), "issue_url": "/2026/06/15/", "beat_title": "Markets",
     "lead_in": "BTC reclaims $60k", "text": "It went up.", "slug": "btc-reclaims-60k"},
    {"date": date(2026, 6, 17), "issue_url": "/2026/06/17/", "beat_title": "Security Desk",
     "lead_in": "Bridge drained for $40M", "text": "An exploit.", "slug": "bridge-drained"},
]


class TestPrompt:
    def test_numbers_and_tags_each_story(self):
        p = wk._build_prompt(STORIES)
        assert "1. [" in p and "Markets" in p and "BTC reclaims $60k" in p
        assert "2. [" in p and "Security Desk" in p


class TestBuildRecap:
    def test_maps_indices_to_real_deep_links(self, monkeypatch):
        monkeypatch.setattr(wk, "_ask_claude", lambda msg: {
            "intro": "A volatile week.",
            "stories": [{"i": 2, "why": "biggest hack of the month"},
                        {"i": 1, "why": "the bottom call landed"}],
        })
        out = wk.build_recap(STORIES)
        assert out["intro"] == "A volatile week."
        assert out["stories"][0] == {
            "headline": "Bridge drained for $40M",
            "why": "biggest hack of the month",
            "link": "/2026/06/17/#bridge-drained",
            "date": date(2026, 6, 17),
        }
        assert out["stories"][1]["link"] == "/2026/06/15/#btc-reclaims-60k"

    def test_drops_out_of_range_and_duplicate_indices(self, monkeypatch):
        monkeypatch.setattr(wk, "_ask_claude", lambda msg: {
            "intro": "x",
            "stories": [{"i": 99, "why": "hallucinated"},
                        {"i": 1, "why": "real"},
                        {"i": 1, "why": "dup"}],
        })
        out = wk.build_recap(STORIES)
        assert [s["why"] for s in out["stories"]] == ["real"]

    def test_empty_selection_yields_no_stories(self, monkeypatch):
        monkeypatch.setattr(wk, "_ask_claude", lambda msg: {"intro": "", "stories": []})
        assert wk.build_recap(STORIES)["stories"] == []


class TestWeekStories:
    def test_reads_front_matter_beats(self, tmp_path, monkeypatch):
        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2026-06-15-cryptoccino.md").write_text(
            "---\n"
            "date: 2026-06-15\n"
            "beats:\n"
            "- id: the_tape\n"
            "  title: Markets\n"
            "  items:\n"
            "  - lead_in: BTC reclaims $60k\n"
            "    text: It went up.\n"
            "    slug: btc-reclaims-60k\n"
            "---\n\nbody\n"
        )
        monkeypatch.setattr(wk, "POSTS_DIR", str(posts))
        stories = wk._week_stories()
        assert len(stories) == 1
        s = stories[0]
        assert s["lead_in"] == "BTC reclaims $60k"
        assert s["issue_url"] == "/2026/06/15/"
        assert s["slug"] == "btc-reclaims-60k"
        assert s["beat_title"] == "Markets"

    def test_skips_items_missing_lead_or_slug(self, tmp_path, monkeypatch):
        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2026-06-16-cryptoccino.md").write_text(
            "---\n"
            "date: 2026-06-16\n"
            "beats:\n"
            "- id: the_tape\n"
            "  title: Markets\n"
            "  items:\n"
            "  - lead_in: ''\n"
            "    text: no headline\n"
            "    slug: x\n"
            "---\n\nbody\n"
        )
        monkeypatch.setattr(wk, "POSTS_DIR", str(posts))
        assert wk._week_stories() == []

    def test_malformed_front_matter_is_skipped_not_crashed(self, tmp_path, monkeypatch):
        posts = tmp_path / "_posts"
        posts.mkdir()
        # no front-matter fence, and broken YAML — must be skipped, not raise.
        (posts / "2026-06-14-cryptoccino.md").write_text("just a body, no front matter\n")
        (posts / "2026-06-15-cryptoccino.md").write_text("---\nbeats: [unclosed\n---\nbody\n")
        monkeypatch.setattr(wk, "POSTS_DIR", str(posts))
        assert wk._week_stories() == []
