"""Integration tests for pipeline.run end-to-end orchestration.

External services (Anthropic, CoinMarketCap, RSS feeds) are patched at the
function level. SQLite uses a real tmp file. The filesystem write goes to
a tmp _posts/ directory, so the run produces a real markdown file we can
inspect.
"""

import datetime as dt
import logging
import sqlite3
from unittest.mock import MagicMock

import pytest

from pipeline import run as run_mod
from pipeline import store


SAMPLE_ITEM = {
    "source_id": "coindesk",
    "category": "crypto",
    "title": "BTC dips",
    "link": "https://example.com/btc",
    "summary": "Bitcoin fell on macro data.",
    "published": dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc),
}

SAMPLE_CURATED = {
    "pour": "Quiet morning.",
    "today": [{"teaser": "btc dips", "beat": "Markets"}],
    "lead": None,
    "beats": [
        {"id": "the_tape", "title": "Markets", "items": [
            {"lead_in": "BTC dips.", "text": "Explainer.",
             "links": [{"source_id": "coindesk",
                        "url": "https://example.com/btc"}]},
        ]},
    ],
    "brewing": [],
    "last_sip": "Done.",
}

SAMPLE_PRICES = [
    {"ticker": "BTC", "price": 60000, "change_24h": -1.0,
     "spark": [1.0, 2.0, 3.0]},
]


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    db = tmp_path / "seen.db"
    monkeypatch.setattr(store, "DB_PATH", str(db))
    return db


@pytest.fixture
def posts_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "_posts").mkdir()
    return tmp_path / "_posts"


def _stub_externals(
    monkeypatch,
    items,
    curated=SAMPLE_CURATED,
    prices=SAMPLE_PRICES,
    card_result="/tmp/fake-card.png",
    fng=None,
):
    monkeypatch.setattr(run_mod, "fetch_feeds", lambda: items)
    monkeypatch.setattr(run_mod, "curate", lambda new, fng=None: curated)
    monkeypatch.setattr(run_mod, "fetch_prices", lambda: prices)
    monkeypatch.setattr(run_mod, "fetch_fng", lambda: fng)
    # Stub card generation so tests don't depend on font + icon assets.
    monkeypatch.setattr(
        run_mod, "generate_card", lambda lead, pour, date, out_path: card_result
    )
    monkeypatch.setattr(
        run_mod, "generate_section_card",
        lambda title, note, date, out_path: out_path,
    )
    # And neutralise the shutil.copyfile call that follows in _generate_card_for.
    import shutil
    monkeypatch.setattr(shutil, "copyfile", lambda src, dst: None)


class TestEarlyExit:
    def test_no_items_skips_curate_render_mark(
        self, fresh_db, posts_dir, monkeypatch, caplog
    ):
        monkeypatch.setattr(run_mod, "fetch_feeds", lambda: [])
        boom = MagicMock(side_effect=AssertionError("must not be called"))
        monkeypatch.setattr(run_mod, "curate", boom)
        monkeypatch.setattr(run_mod, "fetch_prices", boom)
        monkeypatch.setattr(run_mod, "render_post", boom)
        monkeypatch.setattr(run_mod, "mark_seen", boom)

        caplog.set_level(logging.INFO)
        run_mod.main()

        assert "Nothing new today" in caplog.text
        assert list(posts_dir.glob("*.md")) == []
        boom.assert_not_called()

    def test_all_items_already_seen_also_skips(
        self, fresh_db, posts_dir, monkeypatch, caplog
    ):
        # Pre-seed the DB so the only fetched item is already known.
        store.init_db()
        store.mark_seen([SAMPLE_ITEM])

        monkeypatch.setattr(run_mod, "fetch_feeds", lambda: [SAMPLE_ITEM])
        boom = MagicMock(side_effect=AssertionError("must not be called"))
        monkeypatch.setattr(run_mod, "curate", boom)
        monkeypatch.setattr(run_mod, "fetch_prices", boom)
        monkeypatch.setattr(run_mod, "render_post", boom)

        caplog.set_level(logging.INFO)
        run_mod.main()

        assert "Nothing new today" in caplog.text
        assert list(posts_dir.glob("*.md")) == []

    def test_skips_when_todays_post_already_exists(
        self, fresh_db, posts_dir, monkeypatch, caplog
    ):
        # Drop a stub post for today on disk — simulates a previous run
        # having already written one. The second run must no-op rather
        # than overwriting it.
        import datetime as dt
        today_post = posts_dir / f"{dt.date.today().isoformat()}-cryptoccino.md"
        today_post.write_text("already published")

        boom = MagicMock(side_effect=AssertionError("must not be called"))
        monkeypatch.setattr(run_mod, "fetch_feeds", boom)
        monkeypatch.setattr(run_mod, "filter_new", boom)
        monkeypatch.setattr(run_mod, "curate", boom)
        monkeypatch.setattr(run_mod, "fetch_prices", boom)
        monkeypatch.setattr(run_mod, "render_post", boom)
        monkeypatch.setattr(run_mod, "mark_seen", boom)

        caplog.set_level(logging.INFO)
        run_mod.main()

        assert "first-run-wins" in caplog.text
        # Stub content untouched.
        assert today_post.read_text() == "already published"
        boom.assert_not_called()


class TestHappyPath:
    def test_writes_post_with_expected_sections(
        self, fresh_db, posts_dir, monkeypatch
    ):
        _stub_externals(monkeypatch, [SAMPLE_ITEM])

        run_mod.main()

        posts = list(posts_dir.glob("*.md"))
        assert len(posts) == 1
        content = posts[0].read_text()
        assert content.startswith("---\nlayout: issue\n")
        # Section card present, so the beat heading is replaced by the banner.
        assert '<img class="section-card"' in content
        assert "## Markets" not in content
        assert "BTC dips." in content
        assert '<section class="prices">' in content
        assert "BTC" in content
        assert "> **Last sip.** Done." in content

    def test_marks_filtered_items_seen(self, fresh_db, posts_dir, monkeypatch):
        _stub_externals(monkeypatch, [SAMPLE_ITEM])
        run_mod.main()
        with sqlite3.connect(str(fresh_db)) as conn:
            rows = conn.execute(
                "SELECT link, source_id FROM seen"
            ).fetchall()
        assert rows == [(SAMPLE_ITEM["link"], SAMPLE_ITEM["source_id"])]

    def test_rerun_is_idempotent(self, fresh_db, posts_dir, monkeypatch, caplog):
        _stub_externals(monkeypatch, [SAMPLE_ITEM])
        run_mod.main()

        # Second run on the same day: today's post already on disk,
        # must early-exit via the first-run-wins guard before fetch.
        caplog.clear()
        boom = MagicMock(side_effect=AssertionError("must not be called"))
        monkeypatch.setattr(run_mod, "fetch_feeds", boom)
        monkeypatch.setattr(run_mod, "curate", boom)
        monkeypatch.setattr(run_mod, "render_post", boom)
        monkeypatch.setattr(run_mod, "fetch_prices", boom)
        caplog.set_level(logging.INFO)
        run_mod.main()

        assert "first-run-wins" in caplog.text


class TestMarketsResilience:
    def test_empty_markets_still_writes_post_without_prices(
        self, fresh_db, posts_dir, monkeypatch
    ):
        _stub_externals(monkeypatch, [SAMPLE_ITEM], prices=None)

        run_mod.main()

        posts = list(posts_dir.glob("*.md"))
        assert len(posts) == 1
        content = posts[0].read_text()
        assert '<section class="prices">' not in content
        # Section card replaces the H2 even when the price strip is missing.
        assert '<img class="section-card"' in content


class TestCardsResilience:
    def test_card_path_lands_in_front_matter_on_success(
        self, fresh_db, posts_dir, monkeypatch
    ):
        _stub_externals(monkeypatch, [SAMPLE_ITEM])
        run_mod.main()
        post = next(posts_dir.glob("*.md"))
        assert "card: /assets/cards/" in post.read_text()

    def test_card_failure_still_writes_post(
        self, fresh_db, posts_dir, monkeypatch
    ):
        _stub_externals(monkeypatch, [SAMPLE_ITEM], card_result=None)
        run_mod.main()
        posts = list(posts_dir.glob("*.md"))
        assert len(posts) == 1
        content = posts[0].read_text()
        # Hero card failure doesn't kill section cards; banner still present.
        assert '<img class="section-card"' in content
        assert "card:" not in content

    def test_section_card_replaces_beat_heading(
        self, fresh_db, posts_dir, monkeypatch
    ):
        _stub_externals(monkeypatch, [SAMPLE_ITEM])
        run_mod.main()
        post = next(posts_dir.glob("*.md"))
        content = post.read_text()
        assert '<img class="section-card"' in content
        assert "the_tape" in content
        # Banner carries the beat name; H2 heading is dropped.
        assert "## Markets" not in content
