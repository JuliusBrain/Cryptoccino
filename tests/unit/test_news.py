"""Unit tests for pipeline.news.build_news."""

import datetime as dt

from pipeline.news import build_news


def _item(link, mins_ago, source="coindesk", title="Headline"):
    return {
        "link": link,
        "source_id": source,
        "title": title,
        "published": dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=mins_ago),
    }


class TestBuildNews:
    def test_newest_first_and_shape(self):
        out = build_news([_item("https://a/1", 30), _item("https://a/2", 5)])
        assert [n["link"] for n in out] == ["https://a/2", "https://a/1"]
        assert set(out[0]) == {"title", "link", "source", "ts"}
        assert isinstance(out[0]["ts"], int)

    def test_drops_non_http_and_duplicates(self):
        out = build_news([
            _item("https://a/1", 5),
            _item("https://a/1", 6),      # dup link
            _item("ftp://x/1", 1),         # non-http
            _item("javascript:alert(1)", 1),
        ])
        assert [n["link"] for n in out] == ["https://a/1"]

    def test_drops_items_outside_window(self):
        out = build_news([_item("https://a/new", 5), _item("https://a/old", 60 * 13)])
        assert [n["link"] for n in out] == ["https://a/new"]

    def test_caps_to_max_items(self):
        out = build_news([_item(f"https://a/{i}", i) for i in range(60)])
        assert len(out) == 40
