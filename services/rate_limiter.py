from dataclasses import dataclass

from django.core.cache import cache
from django.utils.timezone import now


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int


class RateLimiter:
    cache_format = "rl:%(scope)s:%(key)s"

    @staticmethod
    def hit(scope: str, key: str, expiration: int) -> RateLimitResult:

        cache_key = RateLimiter.cache_format % {"scope": scope, "key": key}

        is_blocked = cache.get(cache_key)

        if is_blocked:
            return RateLimitResult(
                allowed=False, remaining=int(is_blocked - now().timestamp())
            )

        cache.set(cache_key, now().timestamp() + expiration, timeout=expiration)

        return RateLimitResult(allowed=True, remaining=0)
