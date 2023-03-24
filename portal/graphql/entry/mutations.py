import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from ...attribute import AttributeType
from ...attribute.models import Attribute
from ...core.permissions import EntryPermissions
from ...entry import models
from ..attribute.types import AttributeValueInput
from ..attribute.utils import AttributeAssignmentMixin
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from ..core.utils import validate_slug_and_generate_if_needed
from .enums import EntryTypeEnum
from .types import Category, Entry


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


class EntryCreate(ModelMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        input = EntryInput(required=True)

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry

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


class EntryUpdate(ModelMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        id = graphene.ID()
        input = EntryInput(required=True)

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry


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


class CategoryInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    type = EntryTypeEnum()


class CategoryCreate(ModelMutation):
    category = graphene.Field(Category)

    class Arguments:
        input = CategoryInput(required=True)

    class Meta:
        model = models.Category
        permissions = (EntryPermissions.MANAGE_CATEGORIES,)
        object_type = Category

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


class CategoryUpdate(ModelMutation):
    category = graphene.Field(Category)

    class Arguments:
        id = graphene.ID()
        input = CategoryInput(required=True)

    class Meta:
        model = models.Category
        permissions = (EntryPermissions.MANAGE_CATEGORIES,)
        object_type = Category


class CategoryDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Category
        permissions = (EntryPermissions.MANAGE_CATEGORIES,)
        object_type = Category


class CategoryBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of category IDs to delete."
        )

    class Meta:
        description = "Deletes categories."
        model = models.Category
        object_type = Category
        permissions = (EntryPermissions.MANAGE_CATEGORIES,)
