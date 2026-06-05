"""Unit tests for pipeline.store."""

import datetime as dt
import sqlite3

import pytest

from pipeline import store


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "seen.db"
    monkeypatch.setattr(store, "DB_PATH", str(path))
    return str(path)


class TestHash:
    def test_stable_for_same_link(self):
        assert store._hash("https://x.example/a") == store._hash("https://x.example/a")

    def test_different_for_different_links(self):
        assert store._hash("https://x.example/a") != store._hash("https://x.example/b")

    def test_is_hex_string(self):
        h = store._hash("https://x.example/a")
        assert len(h) == 40
        int(h, 16)  # raises if not hex


class TestInitDb:
    def test_creates_seen_table(self, db_path):
        store.init_db()
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='seen'"
            ).fetchone()
        assert row == ("seen",)

    def test_idempotent(self, db_path):
        store.init_db()
        store.init_db()  # second call must not raise

    def test_creates_parent_dir(self, tmp_path, monkeypatch):
        path = tmp_path / "nested" / "deep" / "x.db"
        monkeypatch.setattr(store, "DB_PATH", str(path))
        store.init_db()
        assert path.exists()


class TestFilterNew:
    def test_returns_all_when_db_empty(self, db_path):
        store.init_db()
        items = [{"link": "https://e.example/1", "source_id": "x"}]
        assert store.filter_new(items) == items

    def test_drops_seen_items(self, db_path):
        store.init_db()
        items = [
            {"link": "https://e.example/1", "source_id": "x"},
            {"link": "https://e.example/2", "source_id": "y"},
        ]
        store.mark_seen([items[0]])
        assert store.filter_new(items) == [items[1]]

    def test_empty_input(self, db_path):
        store.init_db()
        assert store.filter_new([]) == []


class TestMarkSeen:
    def test_inserts_with_today_date(self, db_path):
        store.init_db()
        items = [{"link": "https://e.example/1", "source_id": "coindesk"}]
        store.mark_seen(items)
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT link, source_id, first_seen FROM seen"
            ).fetchone()
        assert row == (
            "https://e.example/1",
            "coindesk",
            dt.date.today().isoformat(),
        )

    def test_idempotent_on_duplicate_link(self, db_path):
        store.init_db()
        items = [{"link": "https://e.example/1", "source_id": "x"}]
        store.mark_seen(items)
        store.mark_seen(items)
        with sqlite3.connect(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        assert count == 1

    def test_empty_input_noop(self, db_path):
        store.init_db()
        store.mark_seen([])
        with sqlite3.connect(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        assert count == 0


class TestRoundTrip:
    def test_mark_then_filter_returns_empty(self, db_path):
        store.init_db()
        items = [
            {"link": "https://e.example/1", "source_id": "a"},
            {"link": "https://e.example/2", "source_id": "b"},
        ]
        store.mark_seen(items)
        assert store.filter_new(items) == []
