import graphene
from django.core.exceptions import ValidationError

from ....core.permissions import EntryPermissions
from ....entry import models
from ...core.mutations import (
    ModelBulkDeleteMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from ...core.types import NonNullList
from ...core.utils import validate_slug_and_generate_if_needed
from ..types import Category


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
