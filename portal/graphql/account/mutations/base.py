import graphene
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ....account import models
from ....account.notifications import send_password_reset_notification
from ....account.utils import retrieve_user_by_email
from ...core.mutations import BaseMutation
from ...plugins.dataloaders import get_plugin_manager_promise


class RequestPasswordReset(BaseMutation):
    class Arguments:
        email = graphene.String(required=True)
        redirect_url = graphene.String(required=True)

    @classmethod
    def clean_user(cls, email):
        user = retrieve_user_by_email(email)
        if not user:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "Não foi encontrado nenhum usuário com este email.",
                    )
                }
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        email = data["email"]
        redirect_url = data["redirect_url"]
        user = cls.clean_user(email)
        manager = get_plugin_manager_promise(info.context).get()
        send_password_reset_notification(user, redirect_url, manager)
        return RequestPasswordReset()


class SetPassword(BaseMutation):
    class Arguments:
        token = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def clean_user(cls, email):
        user = retrieve_user_by_email(email)
        if not user:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "Não foi encontrado nenhum usuário com este email.",
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
