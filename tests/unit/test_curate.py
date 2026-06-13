"""Unit tests for pipeline.curate."""

import datetime as dt
import json
from unittest.mock import MagicMock, patch

import anthropic
import httpx
import pytest

from pipeline.curate import (
    MAX_ATTEMPTS_PER_MODEL,
    MODELS,
    _reorder_beats,
    _strip_fences,
    curate,
)


@pytest.fixture(autouse=True)
def _no_sleep():
    """Skip real backoff sleeps so the retry tests stay instant."""
    with patch("pipeline.llm.time.sleep"):
        yield


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


def _resp(text):
    """A fake messages.create() response carrying `text` and a usage block."""
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    response.usage = MagicMock(input_tokens=10, output_tokens=20)
    return response


def _patched_anthropic(returned_text):
    """Mock factory for anthropic.Anthropic() whose create() always succeeds."""
    client = MagicMock()
    client.messages.create.return_value = _resp(returned_text)
    return MagicMock(return_value=client)


def _factory(create):
    """Mock factory for anthropic.Anthropic() with a custom create() (Mock)."""
    client = MagicMock()
    client.messages.create = create
    return MagicMock(return_value=client)


def _conn_error():
    return anthropic.APIConnectionError(
        message="boom", request=httpx.Request("POST", "http://x")
    )


def _auth_error():
    return anthropic.AuthenticationError(
        message="bad key",
        response=httpx.Response(401, request=httpx.Request("POST", "http://x")),
        body=None,
    )


class TestCurate:
    def test_returns_parsed_dict(self):
        with patch(
            "pipeline.llm.anthropic.Anthropic",
            _patched_anthropic(json.dumps(FAKE_ISSUE)),
        ):
            result = curate([SAMPLE_ITEM])
        assert result["pour"] == "one dry line"
        assert result["beats"][0]["id"] == "the_tape"

    def test_strips_fences_before_parsing(self):
        fenced = "```json\n" + json.dumps(FAKE_ISSUE) + "\n```"
        with patch("pipeline.llm.anthropic.Anthropic", _patched_anthropic(fenced)):
            result = curate([SAMPLE_ITEM])
        assert result["last_sip"] == "quiet line"

    def test_retries_then_succeeds_on_bad_json(self):
        create = MagicMock(side_effect=[_resp("not json"), _resp(json.dumps(FAKE_ISSUE))])
        with patch("pipeline.llm.anthropic.Anthropic", _factory(create)):
            result = curate([SAMPLE_ITEM])
        assert result["pour"] == "one dry line"
        assert create.call_count == 2

    def test_retries_transient_api_error(self):
        create = MagicMock(side_effect=[_conn_error(), _resp(json.dumps(FAKE_ISSUE))])
        with patch("pipeline.llm.anthropic.Anthropic", _factory(create)):
            result = curate([SAMPLE_ITEM])
        assert result["last_sip"] == "quiet line"
        assert create.call_count == 2

    def test_falls_back_to_haiku(self):
        def _create(**kwargs):
            if kwargs["model"] == "claude-sonnet-4-6":
                return _resp("not json")          # primary never parses
            return _resp(json.dumps(FAKE_ISSUE))  # fallback succeeds
        create = MagicMock(side_effect=_create)
        with patch("pipeline.llm.anthropic.Anthropic", _factory(create)):
            result = curate([SAMPLE_ITEM])
        assert result["beats"][0]["id"] == "the_tape"
        models = {c.kwargs["model"] for c in create.call_args_list}
        assert "claude-haiku-4-5-20251001" in models
        # Sonnet exhausts its attempts, then one Haiku call succeeds.
        assert create.call_count == MAX_ATTEMPTS_PER_MODEL + 1

    def test_raises_after_exhausting_all_models(self):
        create = MagicMock(return_value=_resp("not json at all"))
        with patch("pipeline.llm.anthropic.Anthropic", _factory(create)):
            with pytest.raises(json.JSONDecodeError):
                curate([SAMPLE_ITEM])
        assert create.call_count == MAX_ATTEMPTS_PER_MODEL * len(MODELS)

    def test_auth_error_fails_fast_without_fallback(self):
        create = MagicMock(side_effect=_auth_error())
        with patch("pipeline.llm.anthropic.Anthropic", _factory(create)):
            with pytest.raises(anthropic.AuthenticationError):
                curate([SAMPLE_ITEM])
        assert create.call_count == 1

    def test_uses_sonnet_model(self):
        with patch(
            "pipeline.llm.anthropic.Anthropic",
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
            "pipeline.llm.anthropic.Anthropic",
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
            "pipeline.llm.anthropic.Anthropic",
            _patched_anthropic(json.dumps(unordered)),
        ):
            result = curate([SAMPLE_ITEM])
        assert [b["id"] for b in result["beats"]] == ["the_tape", "on_the_hill"]
