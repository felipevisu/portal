from typing import Optional, cast

from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.utils import timezone
from django.utils.functional import SimpleLazyObject

from portal.core.jwt import get_token_from_request, jwt_decode_with_exception_handler

from ..account.models import User
from .core.context import PortalContext


def get_context_value(request: HttpRequest) -> PortalContext:
    request = cast(PortalContext, request)
    request.dataloaders = {}
    request.allow_replica = getattr(request, "allow_replica", True)
    request.request_time = timezone.now()
    set_auth_on_context(request)
    set_decoded_auth_token(request)
    return request


class RequestWithUser(HttpRequest):
    _cached_user: Optional[User]


def set_decoded_auth_token(request: PortalContext):
    auth_token = get_token_from_request(request)
    if auth_token:
        request.decoded_auth_token = jwt_decode_with_exception_handler(auth_token)
    else:
        request.decoded_auth_token = None


def get_user(request: PortalContext) -> Optional[User]:
    if not hasattr(request, "_cached_user"):
        request._cached_user = cast(Optional[User], authenticate(request=request))
    return request._cached_user


def set_auth_on_context(request: PortalContext):
    if hasattr(request, "app") and request.app:
        request.user = SimpleLazyObject(lambda: None)  # type: ignore
        return request

    def user():
        return get_user(request) or None

    request.user = SimpleLazyObject(user)  # type: ignore