import time

from services.rate_limiter import RateLimiter


def test_hit():
    result = RateLimiter.hit(
        scope="req_auth_code", key="test@example.com", expiration=5
    )

    assert result.allowed is True
    assert result.remaining == 0

    result = RateLimiter.hit(
        scope="req_auth_code", key="test@example.com", expiration=5
    )

    assert result.allowed is False
    assert result.remaining == 4

    time.sleep(2)

    result = RateLimiter.hit(
        scope="req_auth_code", key="test@example.com", expiration=5
    )

    assert result.allowed is False
    assert result.remaining == 2

    time.sleep(3)

    result = RateLimiter.hit(
        scope="req_auth_code", key="test@example.com", expiration=5
    )

    assert result.allowed is True
    assert result.remaining == 0
