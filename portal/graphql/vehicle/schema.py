import graphene

from portal.graphql.core.connection import (
    create_connection_slice, filter_connection_queryset)

from ..core.fields import FilterConnectionField
from .filters import CategoryFilterInput, VehicleFilterInput
from .mutations import (
    CategoryBulkDelete, CategoryCreate, CategoryDelete, CategoryUpdate,
    VehicleBulkDelete, VehicleCreate, VehicleDelete, VehicleUpdate)
from .resolvers import (
    resolve_categories, resolve_category, resolve_vehicle, resolve_vehicles)
from .sorters import CategorySortingInput, VehicleSortingInput
from .types import (
    Category, CategoryCountableConnection, Vehicle, VehicleCountableConnection)


class Query(graphene.ObjectType):
    category = graphene.Field(
        Category,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    categories = FilterConnectionField(
        CategoryCountableConnection,
        sort_by=CategorySortingInput(),
        filter=CategoryFilterInput()
    )
    vehicle = graphene.Field(
        Vehicle,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    vehicles = FilterConnectionField(
        VehicleCountableConnection,
        sort_by=VehicleSortingInput(),
        filter=VehicleFilterInput()
    )

    def resolve_category(self, info, id=None, slug=None):
        return resolve_category(info, id, slug)

    def resolve_categories(self, info, *args, **kwargs):
        qs = resolve_categories()
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, CategoryCountableConnection)

    def resolve_vehicle(self, info, id=None, slug=None):
        return resolve_vehicle(info, id, slug)

    def resolve_vehicles(self, info, *args, **kwargs):
        qs = resolve_vehicles(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, VehicleCountableConnection)


class Mutation(graphene.ObjectType):
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    category_bulk_delete = CategoryBulkDelete.Field()
    vehicle_create = VehicleCreate.Field()
    vehicle_update = VehicleUpdate.Field()
    vehicle_delete = VehicleDelete.Field()
    vehicle_bulk_delete = VehicleBulkDelete.Field()
