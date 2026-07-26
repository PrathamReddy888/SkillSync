"""
Piston code-execution client with retry + timeout.

The MVP called Piston directly inside the request handler with no retry
and a 10s timeout that was easy to miss. This module wraps the call in
`tenacity` for transient failures and uses the configured timeout.
"""
from typing import Any, Dict

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


PISTON_LANGUAGES = {
    "python": "3.10",
    "javascript": "18.15",
    "typescript": "5.0",
    "java": "15.0",
    "c": "10.2",
    "cpp": "10.2",
    "go": "1.16",
    "rust": "1.68",
}


class PistonError(Exception):
    """Raised when the Piston API call fails after retries."""


async def execute_code(code: str, language: str) -> Dict[str, Any]:
    """
    Execute `code` in `language` via the public Piston API.

    Returns a normalised dict:
        {
            "stdout": str,
            "stderr": str,
            "success": bool,
            "exit_code": int | None,
            "language": str,
        }
    """
    settings = get_settings()
    log = get_logger("piston")

    version = PISTON_LANGUAGES.get(language, "*")

    payload = {
        "language": language,
        "version": version,
        "files": [{"content": code}],
    }

    async def _do_call() -> httpx.Response:
        async with httpx.AsyncClient(timeout=settings.piston_timeout_seconds) as client:
            resp = await client.post(settings.piston_api_url, json=payload)
            resp.raise_for_status()
            return resp

    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(2),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=2.0),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
            reraise=True,
        ):
            with attempt:
                resp = await _do_call()
    except (httpx.HTTPStatusError, httpx.RequestError, RetryError) as e:
        log.error("piston_call_failed", language=language, error=str(e))
        raise PistonError(f"Piston API call failed: {e}") from e

    data = resp.json()
    run = data.get("run", {})
    stdout = (run.get("stdout") or "").strip()
    stderr = (run.get("stderr") or "").strip()
    exit_code = run.get("code")

    return {
        "stdout": stdout,
        "stderr": stderr,
        "success": exit_code == 0 and not stderr,
        "exit_code": exit_code,
        "language": language,
    }
