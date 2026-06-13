"""Shared Anthropic call helper.

One client + one retry/backoff/fallback loop, used by all three Claude callers:
curate (Sonnet, Haiku fallback), news_digest (Haiku) and market_context (Haiku).
Centralises the model ids, the retryable-vs-fail-fast classification, fence
stripping, and usage logging so that policy lives in exactly one place.

Callers decide what to do on total failure: curate lets the exception propagate
(the run should fail); news_digest/market_context catch it and fall open to cache.
"""

import json
import logging
import time

import anthropic

logger = logging.getLogger(__name__)

# Canonical models (see CLAUDE.md). Sonnet writes the daily brief; Haiku powers
# the cheaper TV digest/context jobs and is the brief's fallback.
SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"

MAX_ATTEMPTS = 3        # per model
BACKOFF_BASE_S = 2


def strip_fences(text):
    """Strip a ```/```json code fence (and surrounding whitespace) if present."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    return text.strip()


def is_retryable(exc):
    """True for transient model failures worth retrying / falling back on.

    A malformed-JSON response counts: the model may produce valid JSON on a
    fresh attempt. Auth/config errors (400/401/403) are NOT retryable — they
    fail fast so a broken key surfaces immediately instead of after backoff.
    """
    if isinstance(exc, json.JSONDecodeError):
        return True
    if isinstance(exc, (
        anthropic.RateLimitError,
        anthropic.APIConnectionError,   # includes APITimeoutError
        anthropic.InternalServerError,
    )):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        code = getattr(exc, "status_code", None)
        return code is not None and (code >= 500 or code == 529)
    return False


def _log_usage(response, model):
    usage = getattr(response, "usage", None)
    if usage is not None:
        logger.info(
            "llm: ok on %s (in=%s, out=%s tokens).",
            model,
            getattr(usage, "input_tokens", "?"),
            getattr(usage, "output_tokens", "?"),
        )


def call(models, system, user, max_tokens, parse=None):
    """Try each model in turn (MAX_ATTEMPTS each, exponential backoff between
    attempts) and return the result; raise the last exception once every model
    is exhausted.

    `parse` (optional) is applied to the joined response text INSIDE the retry
    loop, so a parse failure (e.g. json.JSONDecodeError) triggers a retry and
    then a model fallback — exactly as a transient API error does. Without
    `parse`, the fence-stripped text is returned.

    Text is joined across content blocks (not content[0]) so an empty content
    list or a non-text first block yields "" — which a JSON `parse` turns into a
    retryable JSONDecodeError rather than a fatal IndexError/AttributeError.
    """
    client = anthropic.Anthropic(max_retries=0)   # our loop is the sole retry layer
    request = dict(
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    last_exc = None
    for model in models:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = client.messages.create(model=model, **request)
                raw = "".join(getattr(b, "text", "") for b in (response.content or []))
                result = parse(raw) if parse else strip_fences(raw)
                _log_usage(response, model)
                return result
            except Exception as exc:
                if not is_retryable(exc):
                    raise
                last_exc = exc
                logger.warning(
                    "llm: %s attempt %d/%d failed: %s: %s",
                    model, attempt, MAX_ATTEMPTS, exc.__class__.__name__, exc,
                )
                if attempt < MAX_ATTEMPTS:
                    time.sleep(BACKOFF_BASE_S * 2 ** (attempt - 1))
        logger.warning("llm: %s exhausted; trying next model.", model)

    raise last_exc
