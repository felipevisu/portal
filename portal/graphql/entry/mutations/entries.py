import graphene
from django.core.exceptions import ValidationError
from django.db import transaction

from portal.graphql.channel import ChannelContext
from portal.graphql.core import ResolveInfo

from ....attribute import AttributeType
from ....attribute.models import Attribute
from ....core.permissions import EntryPermissions
from ....entry import models
from ...attribute.types import AttributeValueInput
from ...attribute.utils import AttributeAssignmentMixin
from ...core.mutations import (
    ModelBulkDeleteMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from ...core.types import NonNullList
from ...core.types.common import EntryError
from ...core.utils import validate_slug_and_generate_if_needed
from ..enums import EntryTypeEnum
from ..types import Entry


class EntryInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    type = EntryTypeEnum()
    document_number = graphene.String()
    category = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)
    email = graphene.String()
    phone = graphene.String(required=False)
    address = graphene.String(required=False)
    attributes = NonNullList(AttributeValueInput)
    active = graphene.Boolean()


class EntryCreate(ModelMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        input = EntryInput(required=True)

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry
        error_type_class = EntryError

    @classmethod
    def clean_attributes(cls, attributes, entry_type):
        attributes_qs = Attribute.objects.filter(
            type__in=[AttributeType.VEHICLE_AND_PROVIDER, entry_type]
        )
        attributes = AttributeAssignmentMixin.clean_input(
            attributes, attributes_qs, is_document_attributes=False
        )
        return attributes

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": error})

        attributes = cleaned_input.get("attributes")
        entry_type = cleaned_input.get("type")
        if attributes and entry_type:
            try:
                cleaned_input["attributes"] = cls.clean_attributes(
                    attributes, entry_type
                )
            except ValidationError as exc:
                raise ValidationError({"attributes": exc})

        return cleaned_input

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        with transaction.atomic():
            super()._save_m2m(info, instance, cleaned_data)

            attributes = cleaned_data.get("attributes")
            if attributes:
                AttributeAssignmentMixin.save(instance, attributes)

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root, info, **data)
        entry = getattr(response, cls._meta.return_field_name)

        setattr(
            response,
            cls._meta.return_field_name,
            ChannelContext(node=entry, channel_slug=None),
        )
        return response


class EntryUpdate(EntryCreate):
    entry = graphene.Field(Entry)

    class Arguments:
        id = graphene.ID()
        input = EntryInput(required=True)

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry
        error_type_class = EntryError

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            raise ValidationError({"slug": error})

        attributes = cleaned_input.get("attributes")
        if attributes:
            try:
                cleaned_input["attributes"] = cls.clean_attributes(
                    attributes, instance.type
                )
            except ValidationError as exc:
                raise ValidationError({"attributes": exc})

        return cleaned_input

    @classmethod
    def clean_attributes(cls, attributes, entry_type):
        attributes_qs = Attribute.objects.filter(
            type__in=[AttributeType.VEHICLE_AND_PROVIDER, entry_type]
        )
        attributes = AttributeAssignmentMixin.clean_input(
            attributes, attributes_qs, creation=False, is_document_attributes=False
        )
        return attributes


class EntryDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry


class EntryBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of entries IDs to delete."
        )

    class Meta:
        description = "Deletes entries."
        model = models.Entry
        object_type = Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
