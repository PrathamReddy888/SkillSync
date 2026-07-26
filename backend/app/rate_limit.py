"""
Rate limiter — per-IP sliding-window counter backed by an in-memory dict.

Good enough for a single-instance deployment. For multi-instance, swap
the storage layer for Redis (the public API of `RateLimiter.check()`
stays the same).
"""
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, Tuple

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_per_minute = max_requests_per_minute
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> Tuple[bool, int]:
        """
        Returns (allowed, remaining). If not allowed, raises HTTP 429.

        The window is a sliding 60-second window: we pop entries older
        than 60s, then check the count.
        """
        now = time.monotonic()
        window_start = now - 60.0

        with self._lock:
            bucket = self._hits[key]
            # Evict expired entries
            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= self.max_per_minute:
                remaining = 0
                return False, remaining

            bucket.append(now)
            remaining = self.max_per_minute - len(bucket)
            return True, remaining


# Module-level singleton — configured by the app factory.
_limiter: RateLimiter | None = None


def configure_rate_limiter(max_per_minute: int) -> None:
    global _limiter
    _limiter = RateLimiter(max_requests_per_minute=max_per_minute)


def rate_limit_dependency(request: Request) -> None:
    """
    FastAPI dependency. Apply to any router that needs per-IP limiting.

    Usage:
        from app.rate_limit import rate_limit_dependency
        @router.post("/expensive", dependencies=[Depends(rate_limit_dependency)])
    """
    if _limiter is None:
        return  # limiter not configured (e.g. in tests) → skip

    # Prefer X-Forwarded-For (when behind a proxy); fall back to the
    # direct client address.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        ip = xff.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    allowed, remaining = _limiter.check(ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in a minute.",
            headers={"Retry-After": "60", "X-RateLimit-Remaining": "0"},
        )
