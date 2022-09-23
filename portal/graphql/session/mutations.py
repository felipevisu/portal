import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import SessionPermissions
from ...session import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from ..core.utils import validate_slug_and_generate_if_needed
from .types import Session


class SessionInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    content = graphene.JSONString()
    date = graphene.DateTime(required=False)
    is_published = graphene.Boolean(default=False)


class SessionCreate(ModelMutation):
    session = graphene.Field(Session)

    class Arguments:
        input = SessionInput(required=True)

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)
        object_type = Session

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": error})
        return cleaned_input


class SessionUpdate(ModelMutation):
    entry = graphene.Field(Session)

    class Arguments:
        id = graphene.ID()
        input = SessionInput(required=True)

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)
        object_type = Session


class SessionDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)
        object_type = Session


class SessionBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of sessions IDs to delete."
        )

    class Meta:
        description = "Deletes sessions."
        model = models.Session
        object_type = Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)
