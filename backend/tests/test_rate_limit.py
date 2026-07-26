"""
Tests for the rate limiter.
"""
import time

from app.rate_limit import RateLimiter


def test_allows_under_limit():
    rl = RateLimiter(max_requests_per_minute=3)
    for _ in range(3):
        allowed, _ = rl.check("1.2.3.4")
        assert allowed is True


def test_blocks_over_limit():
    rl = RateLimiter(max_requests_per_minute=2)
    assert rl.check("1.2.3.4")[0] is True
    assert rl.check("1.2.3.4")[0] is True
    allowed, remaining = rl.check("1.2.3.4")
    assert allowed is False
    assert remaining == 0


def test_separate_keys_have_separate_budgets():
    rl = RateLimiter(max_requests_per_minute=1)
    assert rl.check("1.1.1.1")[0] is True
    assert rl.check("1.1.1.1")[0] is False
    # Different IP still has its own budget.
    assert rl.check("2.2.2.2")[0] is True


def test_remaining_decrements():
    rl = RateLimiter(max_requests_per_minute=5)
    for expected_remaining in [4, 3, 2, 1, 0]:
        allowed, remaining = rl.check("9.9.9.9")
        assert allowed is True
        assert remaining == expected_remaining
