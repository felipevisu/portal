import graphene
from graphene_django.filter import DjangoFilterConnectionField

from ..utils.sorting import sort_queryset_resolver
from .mutations import (
    CategoryBulkDelete,
    CategoryCreate,
    CategoryDelete,
    CategoryUpdate,
    VehicleBulkDelete,
    VehicleCreate,
    VehicleDelete,
    VehicleUpdate,
)
from .resolvers import (
    resolve_categories,
    resolve_category,
    resolve_vehicle,
    resolve_vehicles,
)
from .sorters import CategorySortingInput
from .types import Category, Vehicle


class Query(graphene.ObjectType):
    category = graphene.Field(
        Category,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    categories = DjangoFilterConnectionField(
        Category,
        sort_by=CategorySortingInput()
    )
    vehicle = graphene.Field(
        Vehicle,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    vehicles = DjangoFilterConnectionField(Vehicle)

    def resolve_category(self, info, id=None, slug=None):
        return resolve_category(info, id, slug)

    def resolve_categories(self, info, *args, **kwargs):
        qs = resolve_categories()
        qs = sort_queryset_resolver(qs, kwargs)
        return qs

    def resolve_vehicles(self, info, *args, **kwargs):
        return resolve_vehicles(info)

    def resolve_vehicle(self, info, id=None, slug=None):
        return resolve_vehicle(info, id, slug)


class Mutation(graphene.ObjectType):
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    category_bulk_delete = CategoryBulkDelete.Field()
    vehicle_create = VehicleCreate.Field()
    vehicle_update = VehicleUpdate.Field()
    vehicle_delete = VehicleDelete.Field()
    vehicle_bulk_delete = VehicleBulkDelete.Field()
