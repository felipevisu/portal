import graphene
from django.core.exceptions import ValidationError

from portal.attribute import AttributeType
from portal.graphql.core.types.common import NonNullList

from ....core.permissions import EntryPermissions
from ....entry import models
from ...core.mutations import ModelDeleteMutation, ModelMutation
from ...core.utils import validate_slug_and_generate_if_needed
from ..types import EntryType


class EntryTypeInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    entry_attributes = NonNullList(
        graphene.ID,
        description="List of attributes shared among all entries.",
        name="entryAttributes",
    )


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
        cls.validate_attributes(cleaned_input)
        return cleaned_input

    @classmethod
    def validate_attributes(cls, cleaned_data):
        errors = {}
        for field in ["entry_attributes"]:
            attributes = cleaned_data.get(field)
            if not attributes:
                continue
            not_valid_attributes = [
                graphene.Node.to_global_id("Attribute", attr.pk)
                for attr in attributes
                if attr.type != AttributeType.ENTRY_TYPE
            ]
            if not_valid_attributes:
                errors[field] = ValidationError(
                    "Only Entry type attributes are allowed.",
                    params={"attributes": not_valid_attributes},
                )
        if errors:
            raise ValidationError(errors)

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        entry_attributes = cleaned_data.get("entry_attributes")
        if entry_attributes is not None:
            instance.entry_attributes.set(entry_attributes)


class EntryTypeUpdate(EntryTypeCreate):
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
