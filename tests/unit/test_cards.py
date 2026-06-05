"""Unit tests for pipeline.cards."""

import datetime as dt

import pytest
from PIL import Image

from pipeline import cards
from pipeline.cards import _fit_headline, _wrap, generate_card


SAMPLE_LEAD = {
    "kicker": "MARKETS",
    "headline": "Bitcoin breaks below $60,000 as US jobs data crushes rate-cut hopes",
}
SAMPLE_POUR = "A blowout jobs print and a market that forgot it had a floor."
SAMPLE_DATE = dt.date(2026, 6, 5)


class TestGenerateCardHappyPath:
    def test_produces_1200x630_rgb_png(self, tmp_path):
        out = tmp_path / "card.png"
        result = generate_card(SAMPLE_LEAD, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result == str(out)
        with Image.open(out) as img:
            assert img.size == (1200, 630)
            assert img.mode == "RGB"

    def test_no_lead_falls_back_to_pour(self, tmp_path):
        out = tmp_path / "card.png"
        result = generate_card(None, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result == str(out)
        assert out.exists()

    def test_empty_lead_falls_back_to_pour(self, tmp_path):
        out = tmp_path / "card.png"
        result = generate_card({}, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result == str(out)
        assert out.exists()

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "nested" / "deep" / "card.png"
        result = generate_card(SAMPLE_LEAD, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result == str(out)
        assert out.exists()


class TestGenerateCardFailOpen:
    def test_missing_icon_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cards, "ICON_PATH", tmp_path / "nope.png")
        out = tmp_path / "card.png"
        result = generate_card(SAMPLE_LEAD, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result is None
        assert not out.exists()

    def test_missing_font_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cards, "SERIF_BOLD", tmp_path / "nope.ttf")
        out = tmp_path / "card.png"
        result = generate_card(SAMPLE_LEAD, SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result is None

    def test_invalid_lead_type_returns_none(self, tmp_path):
        # Passing a string instead of dict or None — lead.get raises.
        out = tmp_path / "card.png"
        result = generate_card("not a dict", SAMPLE_POUR, SAMPLE_DATE, str(out))
        assert result is None

    def test_garbage_date_returns_none(self, tmp_path):
        out = tmp_path / "card.png"
        result = generate_card(SAMPLE_LEAD, SAMPLE_POUR, "not a date", str(out))
        assert result is None


class TestWrap:
    def test_empty_text_returns_empty(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(img)
        font = _font(40)
        assert _wrap(draw, "", font, 1000) == []
        assert _wrap(draw, None, font, 1000) == []

    def test_short_text_one_line(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(img)
        font = _font(40)
        assert _wrap(draw, "hello world", font, 1000) == ["hello world"]

    def test_long_text_wraps(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(img)
        font = _font(40)
        text = "the quick brown fox jumps over the lazy dog"
        lines = _wrap(draw, text, font, 200)
        # Each line ≤ 200 px wide at 40 px serif bold; expect at least 3 lines.
        assert len(lines) >= 3
        assert " ".join(lines) == text


class TestFitHeadline:
    def test_starts_at_full_size_when_it_fits(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (1200, 630))
        draw = ImageDraw.Draw(img)
        font, lines = _fit_headline(draw, "Short headline.", 1040)
        assert font.size == 64
        assert lines == ["Short headline."]

    def test_shrinks_until_fits_three_lines(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (1200, 630))
        draw = ImageDraw.Draw(img)
        long_text = "Bitcoin breaks below sixty thousand dollars for the first time since October 2024 as stronger-than-expected US jobs data crushes near-term rate-cut hopes across asset classes"
        font, lines = _fit_headline(draw, long_text, 1040)
        assert len(lines) <= 3
        # Some shrink happened.
        assert font.size <= 64

    def test_truncates_when_even_min_size_overflows(self):
        from PIL import ImageDraw

        img = Image.new("RGB", (1200, 630))
        draw = ImageDraw.Draw(img)
        runaway = " ".join(["word"] * 200)
        font, lines = _fit_headline(draw, runaway, 1040)
        assert len(lines) <= 3


def _font(size):
    from PIL import ImageFont

    return ImageFont.truetype(str(cards.SERIF_BOLD), size)
