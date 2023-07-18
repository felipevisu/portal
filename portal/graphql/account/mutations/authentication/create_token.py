from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from portal.core.jwt import create_access_token, create_refresh_token
from portal.graphql.core.mutations import BaseMutation

from ...types import User
from .utils import _get_new_csrf_token

UserModel = get_user_model()


class CreateToken(BaseMutation):
    """Mutation that authenticates a user and returns token and user data."""

    class Arguments:
        email = graphene.String(required=True, description="Email of a user.")
        password = graphene.String(required=True, description="Password of a user.")

    class Meta:
        description = "Create JWT token."

    token = graphene.String(description="JWT token, required to authenticate.")
    refresh_token = graphene.String(
        description="JWT refresh token, required to re-generate access token."
    )
    csrf_token = graphene.String(
        description="CSRF token required to re-generate access token."
    )
    user = graphene.Field(User, description="A user instance.")

    @classmethod
    def _retrieve_user_from_credentials(cls, email, password) -> Optional[UserModel]:
        user = UserModel.objects.filter(email=email, is_active=True).first()
        if user and user.check_password(password):
            return user
        return None

    @classmethod
    def get_user(cls, _info, data):
        user = cls._retrieve_user_from_credentials(data["email"], data["password"])
        if not user:
            raise ValidationError(
                {"email": ValidationError("Por favor, insira credenciais válidas")}
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = cls.get_user(info, data)
        additional_paylod = {}

        csrf_token = _get_new_csrf_token()
        refresh_additional_payload = {
            "csrfToken": csrf_token,
        }
        access_token = create_access_token(user, additional_payload=additional_paylod)
        refresh_token = create_refresh_token(
            user, additional_payload=refresh_additional_payload
        )
        setattr(info.context, "refresh_token", refresh_token)
        info.context.user = user
        info.context._cached_user = user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "updated_at"])
        return cls(
            errors=[],
            user=user,
            token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )
