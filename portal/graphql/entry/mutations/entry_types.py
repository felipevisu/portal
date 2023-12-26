import graphene
from django.core.exceptions import ValidationError

from ....core.permissions import EntryPermissions
from ....entry import models
from ...core.mutations import ModelDeleteMutation, ModelMutation
from ...core.utils import validate_slug_and_generate_if_needed
from ..types import EntryType


class EntryTypeInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()


class EntryTypeCreate(ModelMutation):
    entry_type = graphene.Field(EntryType)

    class Arguments:
        input = EntryTypeInput(required=True)

    class Meta:
        model = models.EntryType
        permissions = (EntryPermissions.MANAGE_ENTRY_TYPES,)
        object_type = EntryType

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


class EntryTypeUpdate(ModelMutation):
    entry_type = graphene.Field(EntryType)

    class Arguments:
        id = graphene.ID()
        input = EntryTypeInput(required=True)

    class Meta:
        model = models.EntryType
        permissions = (EntryPermissions.MANAGE_ENTRY_TYPES,)
        object_type = EntryType


class EntryTypeDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.EntryType
        permissions = (EntryPermissions.MANAGE_ENTRY_TYPES,)
        object_type = EntryType
