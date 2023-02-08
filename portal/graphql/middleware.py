from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = authenticate(request=request)
    return request._cached_user


class JWTMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context

        def user():
            return get_user(request) or AnonymousUser()

        request.user = SimpleLazyObject(lambda: user())
        return next(root, info, **kwargs)
