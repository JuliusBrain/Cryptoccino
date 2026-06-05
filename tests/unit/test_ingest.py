"""Unit tests for pipeline.ingest."""

import datetime as dt

import responses

from pipeline.ingest import _parse_published, _strip_html, fetch_feeds


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Sample feed</title>
<link>https://example.com</link>
<description>x</description>
<item>
  <title>Story one</title>
  <link>https://example.com/one</link>
  <description>A &lt;em&gt;brief&lt;/em&gt; summary &amp;amp; more.</description>
  <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
</item>
<item>
  <title>Story two</title>
  <link>https://example.com/two</link>
  <description>Another story.</description>
</item>
</channel>
</rss>"""


class TestStripHtml:
    def test_strips_tags(self):
        assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_unescapes_entities(self):
        assert _strip_html("Smith &amp; Co") == "Smith & Co"

    def test_collapses_whitespace(self):
        assert _strip_html("a   b\n\nc") == "a b c"

    def test_handles_empty_string(self):
        assert _strip_html("") == ""

    def test_handles_none(self):
        assert _strip_html(None) == ""


class TestParsePublished:
    def test_uses_published_parsed(self):
        entry = {"published_parsed": (2024, 1, 15, 10, 30, 0, 0, 0, 0)}
        result = _parse_published(entry)
        assert result == dt.datetime(2024, 1, 15, 10, 30, 0, tzinfo=dt.timezone.utc)

    def test_falls_back_to_updated_parsed(self):
        entry = {"updated_parsed": (2024, 2, 1, 12, 0, 0, 0, 0, 0)}
        result = _parse_published(entry)
        assert result == dt.datetime(2024, 2, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

    def test_prefers_published_over_updated(self):
        entry = {
            "published_parsed": (2024, 1, 1, 0, 0, 0, 0, 0, 0),
            "updated_parsed": (2024, 6, 1, 0, 0, 0, 0, 0, 0),
        }
        assert _parse_published(entry).year == 2024
        assert _parse_published(entry).month == 1

    def test_defaults_to_now_utc(self):
        before = dt.datetime.now(dt.timezone.utc)
        result = _parse_published({})
        after = dt.datetime.now(dt.timezone.utc)
        assert result.tzinfo == dt.timezone.utc
        assert before <= result <= after


class TestFetchFeeds:
    @responses.activate
    def test_normalises_items(self, tmp_path):
        config = tmp_path / "feeds.yaml"
        config.write_text(
            "feeds:\n"
            "  - id: sample\n"
            "    category: crypto\n"
            "    url: https://example.com/feed\n"
        )
        responses.add(
            responses.GET,
            "https://example.com/feed",
            body=SAMPLE_RSS,
            content_type="application/rss+xml",
        )

        items = fetch_feeds(str(config))

        assert len(items) == 2
        first = items[0]
        assert first["source_id"] == "sample"
        assert first["category"] == "crypto"
        assert first["title"] == "Story one"
        assert first["link"] == "https://example.com/one"
        assert "<em>" not in first["summary"]
        assert "brief" in first["summary"]
        assert first["published"].year == 2024
        assert first["published"].tzinfo == dt.timezone.utc

    @responses.activate
    def test_sends_browser_user_agent(self, tmp_path):
        config = tmp_path / "feeds.yaml"
        config.write_text(
            "feeds:\n  - { id: sample, category: x, url: https://example.com/feed }\n"
        )
        responses.add(responses.GET, "https://example.com/feed", body=SAMPLE_RSS)
        fetch_feeds(str(config))
        ua = responses.calls[0].request.headers["User-Agent"]
        assert "Mozilla" in ua

    @responses.activate
    def test_continues_on_single_feed_error(self, tmp_path):
        config = tmp_path / "feeds.yaml"
        config.write_text(
            "feeds:\n"
            "  - { id: dead, category: x, url: https://dead.example/rss }\n"
            "  - { id: live, category: y, url: https://live.example/rss }\n"
        )
        responses.add(responses.GET, "https://dead.example/rss", status=500)
        responses.add(responses.GET, "https://live.example/rss", body=SAMPLE_RSS)

        items = fetch_feeds(str(config))

        assert len(items) == 2
        assert all(it["source_id"] == "live" for it in items)

    @responses.activate
    def test_returns_empty_when_all_feeds_fail(self, tmp_path):
        config = tmp_path / "feeds.yaml"
        config.write_text(
            "feeds:\n  - { id: dead, category: x, url: https://dead.example/rss }\n"
        )
        responses.add(responses.GET, "https://dead.example/rss", status=500)
        assert fetch_feeds(str(config)) == []
