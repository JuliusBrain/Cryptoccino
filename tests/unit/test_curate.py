"""Unit tests for pipeline.curate."""

import datetime as dt
import json
from unittest.mock import MagicMock, patch

import pytest

from pipeline.curate import _reorder_beats, _strip_fences, curate


SAMPLE_ITEM = {
    "source_id": "coindesk",
    "title": "t",
    "summary": "s",
    "link": "https://e.example/a",
    "published": dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc),
}

FAKE_ISSUE = {
    "pour": "one dry line",
    "today": [],
    "lead": None,
    "beats": [
        {"id": "the_tape", "title": "Markets",
         "items": [{"lead_in": "x", "text": "y"}]},
    ],
    "brewing": [],
    "last_sip": "quiet line",
}


class TestStripFences:
    def test_plain_json_unchanged(self):
        assert _strip_fences('{"a": 1}') == '{"a": 1}'

    def test_strips_json_fence(self):
        assert _strip_fences('```json\n{"a": 1}\n```') == '{"a": 1}'

    def test_strips_plain_fence(self):
        assert _strip_fences('```\n{"a": 1}\n```') == '{"a": 1}'

    def test_strips_surrounding_whitespace(self):
        assert _strip_fences('   \n  {"a": 1}  \n') == '{"a": 1}'


class TestReorderBeats:
    def test_canonical_order(self):
        beats = [
            {"id": "on_the_hill", "items": [{"x": 1}]},
            {"id": "the_tape", "items": [{"x": 1}]},
            {"id": "security_desk", "items": [{"x": 1}]},
            {"id": "projects_money", "items": [{"x": 1}]},
        ]
        result = _reorder_beats(beats)
        assert [b["id"] for b in result] == [
            "the_tape", "projects_money", "security_desk", "on_the_hill",
        ]

    def test_drops_empty_items(self):
        beats = [
            {"id": "the_tape", "items": []},
            {"id": "projects_money", "items": [{"x": 1}]},
        ]
        result = _reorder_beats(beats)
        assert [b["id"] for b in result] == ["projects_money"]

    def test_drops_unknown_ids(self):
        beats = [
            {"id": "the_tape", "items": [{"x": 1}]},
            {"id": "made_up", "items": [{"x": 1}]},
        ]
        result = _reorder_beats(beats)
        assert [b["id"] for b in result] == ["the_tape"]

    def test_empty_input(self):
        assert _reorder_beats([]) == []


def _patched_anthropic(returned_text):
    """Helper that builds the mock graph for anthropic.Anthropic()."""
    response = MagicMock()
    response.content = [MagicMock(text=returned_text)]
    client = MagicMock()
    client.messages.create.return_value = response
    return MagicMock(return_value=client)


class TestCurate:
    def test_returns_parsed_dict(self):
        with patch(
            "pipeline.curate.anthropic.Anthropic",
            _patched_anthropic(json.dumps(FAKE_ISSUE)),
        ):
            result = curate([SAMPLE_ITEM])
        assert result["pour"] == "one dry line"
        assert result["beats"][0]["id"] == "the_tape"

    def test_strips_fences_before_parsing(self):
        fenced = "```json\n" + json.dumps(FAKE_ISSUE) + "\n```"
        with patch("pipeline.curate.anthropic.Anthropic", _patched_anthropic(fenced)):
            result = curate([SAMPLE_ITEM])
        assert result["last_sip"] == "quiet line"

    def test_raises_on_bad_json(self):
        with patch(
            "pipeline.curate.anthropic.Anthropic",
            _patched_anthropic("not json at all"),
        ):
            with pytest.raises(json.JSONDecodeError):
                curate([SAMPLE_ITEM])

    def test_uses_sonnet_model(self):
        with patch(
            "pipeline.curate.anthropic.Anthropic",
            _patched_anthropic(json.dumps(FAKE_ISSUE)),
        ) as Anthropic:
            curate([SAMPLE_ITEM])
        client = Anthropic.return_value
        kwargs = client.messages.create.call_args.kwargs
        assert kwargs["model"] == "claude-sonnet-4-6"

    def test_loads_system_prompt_from_file(self):
        # The real prompts/brief_system.md is read on each call. Verify it
        # ends up as the system parameter to messages.create.
        with patch(
            "pipeline.curate.anthropic.Anthropic",
            _patched_anthropic(json.dumps(FAKE_ISSUE)),
        ) as Anthropic:
            curate([SAMPLE_ITEM])
        kwargs = Anthropic.return_value.messages.create.call_args.kwargs
        assert "editor of Cryptoccino" in kwargs["system"]

    def test_reorders_beats_in_response(self):
        unordered = {
            **FAKE_ISSUE,
            "beats": [
                {"id": "on_the_hill", "title": "On the Hill",
                 "items": [{"lead_in": "x", "text": "y"}]},
                {"id": "the_tape", "title": "Markets",
                 "items": [{"lead_in": "x", "text": "y"}]},
            ],
        }
        with patch(
            "pipeline.curate.anthropic.Anthropic",
            _patched_anthropic(json.dumps(unordered)),
        ):
            result = curate([SAMPLE_ITEM])
        assert [b["id"] for b in result["beats"]] == ["the_tape", "on_the_hill"]
