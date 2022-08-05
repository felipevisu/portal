import graphene
from graphene_django import DjangoObjectType

from portal.graphql.core.connection import ContableConnection
from portal.graphql.vehicle.filters import CategoryFilter, VehicleFilter
from portal.vehicle import models


class Vehicle(DjangoObjectType):

    class Meta:
        model = models.Vehicle
        filterset_class = VehicleFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_category(self, info):
        if self.category_id:
            category_id = self.category_id
        else:
            return None
        return info.context.loaders.category_loader.load(category_id)


class VehiclesConnection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        node = Vehicle

    def resolve_total_count(root, info, **kwargs):
        return len(root.edges)


class Category(DjangoObjectType):
    custom_id = graphene.ID()
    vehicles = graphene.relay.ConnectionField(VehiclesConnection)

    class Meta:
        model = models.Category
        filterset_class = CategoryFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_vehicles(self, info, **kwargs):
        return info.context.loaders.vehicles_by_category_loader.load(self.id)

    def resolve_custom_id(self, info):
        return self.id
