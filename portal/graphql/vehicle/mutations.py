import graphene

from ...core.permissions import VehiclePermissions
from ...vehicle import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
from .types import Category, Vehicle


class VehicleInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    document_number = graphene.String()
    category = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)


class VehicleCreate(ModelMutation):
    vehicle = graphene.Field(Vehicle)

    class Arguments:
        input = VehicleInput(required=True)

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)


class VehicleUpdate(ModelMutation):
    vehicle = graphene.Field(Vehicle)

    class Arguments:
        id = graphene.ID()
        input = VehicleInput(required=True)

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_VEHICLES,)


class VehicleDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Vehicle
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)


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


class CategoryUpdate(ModelMutation):
    category = graphene.Field(Category)

    class Arguments:
        id = graphene.ID()
        input = CategoryInput(required=True)

    class Meta:
        model = models.Category
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)


class CategoryDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Category
        permissions = (VehiclePermissions.MANAGE_CATEGORIES,)


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
