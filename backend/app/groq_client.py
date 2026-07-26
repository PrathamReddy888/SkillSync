"""
Groq client wrapper with retry, timeout, and JSON-extraction helpers.

The MVP `main.py` called Groq inline with `print()` on errors and no
retry. This module provides a single `call_groq()` function that:

  * Uses `tenacity` for exponential backoff on transient failures.
  * Enforces a per-call timeout via `httpx.AsyncClient`.
  * Strips markdown code fences from the response before parsing.
  * Returns parsed JSON when `json_mode=True`, raising
    `GroqJSONError` on malformed output so the caller can fall back.
"""
import json
import re
from typing import Any, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    RetryError,
)

from app.config import get_settings
from app.logging import get_logger


class GroqError(Exception):
    """Raised when the Groq API call fails after retries."""


class GroqJSONError(GroqError):
    """Raised when Groq returns a response that isn't valid JSON."""


_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?|\n?```\s*$", re.MULTILINE)


def _strip_code_fences(text: str) -> str:
    """Strip markdown ```json ... ``` fences if present."""
    return _CODE_FENCE_RE.sub("", text).strip()


async def call_groq(
    prompt: str,
    *,
    system: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Any:
    """
    Call the Groq chat-completions API.

    Args:
        prompt: User message content.
        system: Optional system prompt.
        json_mode: If True, parse the response as JSON and return the
            parsed object. Raises `GroqJSONError` on malformed output.
        temperature: Sampling temperature.
        max_tokens: Optional max output tokens.

    Returns:
        The raw text response, OR a parsed JSON object if `json_mode`.

    Raises:
        GroqError: upstream HTTP failure after retries.
        GroqJSONError: response couldn't be parsed as JSON.
    """
    settings = get_settings()
    log = get_logger("groq")

    if not settings.groq_configured:
        raise GroqError("GROQ_API_KEY is not configured.")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    url = "https://api.groq.com/openai/v1/chat/completions"

    async def _do_call() -> httpx.Response:
        async with httpx.AsyncClient(timeout=settings.groq_timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp

    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
            reraise=True,
        ):
            with attempt:
                resp = await _do_call()
    except (httpx.HTTPStatusError, httpx.RequestError, RetryError) as e:
        log.error("groq_call_failed", error=str(e))
        raise GroqError(f"Groq API call failed: {e}") from e

    data = resp.json()
    text = data["choices"][0]["message"]["content"].strip()
    text = _strip_code_fences(text)

    if not json_mode:
        return text

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        log.error("groq_json_parse_failed", error=str(e), preview=text[:200])
        raise GroqJSONError(f"Groq response was not valid JSON: {e}") from e
