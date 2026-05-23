import pytest
from django.http import HttpRequest

from services.rate_limiter import RateLimiter

scope = "verify_auth_code"


@pytest.fixture
def http_request():
    _request = HttpRequest()
    _request.META["REMOTE_ADDR"] = "127.0.0.1"
    return _request


def test_check_returns_none_when_not_blocked(http_request):

    RateLimiter.reset(scope=scope, request=http_request)

    result = RateLimiter.check(scope=scope, request=http_request)

    assert result.allowed is True

    for _ in range(5):
        RateLimiter.register_failure(scope=scope, request=http_request)

    result = RateLimiter.check(scope=scope, request=http_request)

    assert result.allowed is False

    RateLimiter.reset(scope=scope, request=http_request)

    result = RateLimiter.check(scope=scope, request=http_request)

    assert result.allowed is True
