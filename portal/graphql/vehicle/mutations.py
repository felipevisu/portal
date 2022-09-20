import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import VehiclePermissions
from ...vehicle import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from ..core.utils import validate_slug_and_generate_if_needed
from .types import Category, Vehicle


class VehicleInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    document_number = graphene.String()
    category = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)
    email = graphene.String(required=False)
    phone = graphene.String(required=False)
    address = graphene.String(required=False)


class VehicleCreate(ModelMutation):
    vehicle = graphene.Field(Vehicle)

    class Arguments:
        input = VehicleInput(required=True)

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)
        object_type = Vehicle

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


class VehicleUpdate(ModelMutation):
    vehicle = graphene.Field(Vehicle)

    class Arguments:
        id = graphene.ID()
        input = VehicleInput(required=True)

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)
        object_type = Vehicle


class VehicleDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)
        object_type = Vehicle


class VehicleBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of vehicles IDs to delete."
        )

    class Meta:
        description = "Deletes vehicles."
        model = models.Vehicle
        object_type = Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)


class CategoryInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()


class CategoryCreate(ModelMutation):
    category = graphene.Field(Category)

    class Arguments:
        input = CategoryInput(required=True)

    class Meta:
        model = models.Category
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)
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
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)
        object_type = Category


class CategoryDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Category
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)
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
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)
