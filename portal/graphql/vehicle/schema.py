import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .mutations import (
    CategoryCreate,
    CategoryDelete,
    CategoryUpdate,
    VehicleCreate,
    VehicleDelete,
    VehicleUpdate,
)
from .resolvers import resolve_category, resolve_vehicle, resolve_vehicles
from .types import Category, Vehicle


class Query(graphene.ObjectType):
    category = graphene.Field(
        Category,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    categories = DjangoFilterConnectionField(Category)
    vehicle = graphene.Field(
        Vehicle,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    vehicles = DjangoFilterConnectionField(Vehicle)

    def resolve_category(self, info, id=None, slug=None):
        return resolve_category(info, id, slug)

    def resolve_vehicles(self, info, *args, **kwargs):
        return resolve_vehicles(info)

    def resolve_vehicle(self, info, id=None, slug=None):
        return resolve_vehicle(info, id, slug)


class Mutation(graphene.ObjectType):
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    vehicle_create = VehicleCreate.Field()
    vehicle_update = VehicleUpdate.Field()
    vehicle_delete = VehicleDelete.Field()
