import graphene
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ....account import models
from ....account.notifications import send_password_reset_notification
from ....account.utils import retrieve_user_by_email
from ...core.mutations import BaseMutation


class RequestPasswordReset(BaseMutation):
    class Arguments:
        email = graphene.String(
            required=True,
            description="Email of the user that will be used for password recovery.",
        )
        redirect_url = graphene.String(
            required=True,
            description=(
                "URL of a view where users should be redirected to "
                "reset the password. URL in RFC 1808 format."
            ),
        )

    @classmethod
    def clean_user(cls, email):
        user = retrieve_user_by_email(email)
        if not user:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "User with this email doesn't exist",
                    )
                }
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        email = data["email"]
        redirect_url = data["redirect_url"]
        user = cls.clean_user(email)
        send_password_reset_notification(user, redirect_url)
        return RequestPasswordReset()


class SetPassword(BaseMutation):
    class Arguments:
        token = graphene.String(
            description="A one-time token required to set the password.", required=True
        )
        email = graphene.String(required=True, description="Email of a user.")
        password = graphene.String(required=True, description="Password of a user.")

    @classmethod
    def clean_user(cls, email):
        user = retrieve_user_by_email(email)
        if not user:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "User with this email doesn't exist",
                    )
                }
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        email = data["email"]
        token = data["token"]
        password = data["password"]
        cls._set_password_for_user(email, password, token)
        return RequestPasswordReset()

    @classmethod
    def _set_password_for_user(cls, email, password, token):
        try:
            user = models.User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise ValidationError({"email": ValidationError("User doesn't exist")})
        if not default_token_generator.check_token(user, token):
            raise ValidationError({"token": ValidationError("Invalid token")})
        try:
            password_validation.validate_password(password, user)
        except ValidationError as error:
            raise ValidationError({"password": error})
        user.set_password(password)
        user.save(update_fields=["password", "updated_at"])
