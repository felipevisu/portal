import pytest
from django.core.handlers.base import BaseHandler
from freezegun import freeze_time

from ..jwt import (
    JWT_REFRESH_TOKEN_COOKIE_NAME,
    JWT_REFRESH_TYPE,
    create_refresh_token,
    jwt_encode,
    jwt_user_payload,
)

pytestmark = pytest.mark.django_db


@freeze_time("2020-03-18 12:00:00")
def test_jwt_refresh_token_middleware(rf, staff_user, settings):
    refresh_token = create_refresh_token(staff_user)
    settings.MIDDLEWARE = [
        "portal.core.middleware.jwt_refresh_token_middleware",
    ]
    request = rf.request()
    request.refresh_token = refresh_token
    handler = BaseHandler()
    handler.load_middleware()
    response = handler.get_response(request)
    cookie = response.cookies.get(JWT_REFRESH_TOKEN_COOKIE_NAME)
    assert cookie.value == refresh_token


@freeze_time("2020-03-18 12:00:00")
def test_jwt_refresh_token_middleware_token_without_expire(rf, staff_user, settings):
    settings.JWT_EXPIRE = True
    payload = jwt_user_payload(
        staff_user,
        JWT_REFRESH_TYPE,
        settings.JWT_TTL_REFRESH,
    )
    del payload["exp"]

    refresh_token = jwt_encode(payload)
    settings.MIDDLEWARE = [
        "portal.core.middleware.jwt_refresh_token_middleware",
    ]
    request = rf.request()
    request.refresh_token = refresh_token
    handler = BaseHandler()
    handler.load_middleware()
    response = handler.get_response(request)
    cookie = response.cookies.get(JWT_REFRESH_TOKEN_COOKIE_NAME)
    assert cookie.value == refresh_token
