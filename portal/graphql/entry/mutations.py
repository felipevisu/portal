import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import EntryPermissions
from ...entry import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from ..core.utils import validate_slug_and_generate_if_needed
from .enums import EntryTypeEnum
from .types import Category, Entry


class EntryInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    document_number = graphene.String()
    category = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)
    email = graphene.String(required=False)
    phone = graphene.String(required=False)
    address = graphene.String(required=False)


class EntryCreate(ModelMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        type = EntryTypeEnum()
        input = EntryInput(required=True)

    class Meta:
        model = models.Entry
        permissions = (EntryPermissions.MANAGE_ENTRIES,)
        object_type = Entry

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

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        input = data.get("input")
        instance = models.Entry()
        instance.type = data.get("type")
        cleaned_input = cls.clean_input(info, instance, input)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()
        return EntryCreate(entry=instance)


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
