import graphene
from graphene_django import DjangoObjectType

from ...investment import models
from ..core.connection import ContableConnection
from .dataloaders import ItemsByInvestmentIdLoader

items_loader = ItemsByInvestmentIdLoader()


class Item(DjangoObjectType):

    class Meta:
        model = models.Item
        filter_fields = ['name']
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection


class Investment(DjangoObjectType):
    items = graphene.List(Item)

    class Meta:
        model = models.Investment
        filter_fields = ['month', 'year', 'is_published']
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_items(self, info):
        return items_loader.load(self.id)
