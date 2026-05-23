from dataclasses import dataclass

from django.core.cache import cache
from django.http import HttpRequest
from django.utils.timezone import now
from ipware import get_client_ip


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    """Seconds"""


class RateLimiterConfig:
    _cache_format = "rl:%(scope)s:%(key)s"
    MAX_ATTEMPTS = 5
    BASE_BLOCK_TIME = 30
    MAX_BLOCK_TIME = 60 * 15


class RateLimiter(RateLimiterConfig):
    @staticmethod
    def hit(scope: str, key: str, expiration: int) -> RateLimitResult:

        cache_key = RateLimiterConfig._cache_format % {"scope": scope, "key": key}

        is_blocked = cache.get(cache_key)

        if is_blocked:
            return RateLimitResult(
                allowed=False, remaining=int(is_blocked - now().timestamp())
            )

        cache.set(cache_key, now().timestamp() + expiration, timeout=expiration)

        return RateLimitResult(allowed=True, remaining=0)

    @staticmethod
    def check(
        scope: str,
        request: HttpRequest,
    ):

        if not request:
            return RateLimitResult(allowed=True, remaining=0)

        ip_address, _ = get_client_ip(request)

        cache_key = RateLimiterConfig._cache_format % {
            "scope": scope,
            "key": ip_address,
        }

        blocked_until = cache.get(f"{cache_key}_blocked_until")

        if blocked_until and blocked_until > now().timestamp():
            return RateLimitResult(
                allowed=False, remaining=int(blocked_until - now().timestamp())
            )

        return RateLimitResult(allowed=True, remaining=0)

    @staticmethod
    def register_failure(
        scope: str,
        request: HttpRequest,
        max_attempts: int = RateLimiterConfig.MAX_ATTEMPTS,
        base_block_time: int = RateLimiterConfig.BASE_BLOCK_TIME,
        max_block_time: int = RateLimiterConfig.MAX_BLOCK_TIME,
    ):

        if not request:
            return

        ip_address, _ = get_client_ip(request)

        cache_key = RateLimiterConfig._cache_format % {
            "scope": scope,
            "key": ip_address,
        }

        try:
            count = cache.incr(f"{cache_key}_count")
        except ValueError:
            cache.set(f"{cache_key}_count", 1, timeout=max_block_time)
            count = 1

        if count >= max_attempts:
            exponent = count - max_attempts

            block_duration = min(
                base_block_time * (2**exponent),
                max_block_time,
            )

            blocked_until = now().timestamp() + block_duration

            cache.set(
                f"{cache_key}_blocked_until", blocked_until, timeout=block_duration
            )

    def reset(
        scope: str,
        request: HttpRequest,
    ):

        if not request:
            return

        ip_address, _ = get_client_ip(request)

        cache_key = RateLimiterConfig._cache_format % {
            "scope": scope,
            "key": ip_address,
        }

        cache.delete_many([f"{cache_key}_count", f"{cache_key}_blocked_until"])
