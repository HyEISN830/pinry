from rest_framework.throttling import SimpleRateThrottle

from core.likes import client_ip


class LikeRateThrottle(SimpleRateThrottle):
    scope = None

    def get_cache_key(self, request, view):
        ident = client_ip(request) or self.get_ident(request) or 'unknown'
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }


class LikeMinuteRateThrottle(LikeRateThrottle):
    scope = 'likes_minute'


class LikeDailyRateThrottle(LikeRateThrottle):
    scope = 'likes_day'


class ViewMinuteRateThrottle(LikeRateThrottle):
    scope = 'views_minute'


class ViewDailyRateThrottle(LikeRateThrottle):
    scope = 'views_day'
