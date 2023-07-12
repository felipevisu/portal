from typing import Any, Dict

import jwt
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.module_loading import import_string

JWT_ALGORITHM = "HS256"


class JWTManagerBase:
    @classmethod
    def get_domain(cls) -> str:
        return NotImplemented

    @classmethod
    def encode(cls, payload: dict) -> str:
        return NotImplemented

    @classmethod
    def decode(cls, token: str, verify_expiration: bool = True) -> dict:
        return NotImplemented


class JWTManager(JWTManagerBase):
    @classmethod
    def get_domain(cls) -> str:
        return Site.objects.get_current().domain

    @classmethod
    def encode(cls, payload):
        return jwt.encode(
            payload,
            settings.SECRET_KEY,  # type: ignore
            JWT_ALGORITHM,
        )

    @classmethod
    def decode(
        cls, token: str, verify_expiration=settings.JWT_EXPIRE
    ) -> Dict[str, Any]:
        return jwt.decode(
            token,
            settings.SECRET_KEY,  # type: ignore
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": verify_expiration},
        )


def get_jwt_manager() -> JWTManagerBase:
    return import_string(settings.JWT_MANAGER_PATH)
