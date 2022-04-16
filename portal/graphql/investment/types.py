import graphene
from graphene_django import DjangoObjectType

from ...investment import models
from .dataloaders import ItemsByInvestmentIdLoader

items_loader = ItemsByInvestmentIdLoader()


class Item(DjangoObjectType):

    class Meta:
        model = models.Item
        filter_fields = ['name']
        interfaces = [graphene.relay.Node]


class Investment(DjangoObjectType):
    items = graphene.List(Item)

    class Meta:
        model = models.Investment
        filter_fields = ['mounth', 'year', 'is_published']
        interfaces = [graphene.relay.Node]

    def resolve_items(self, info):
        return items_loader.load(self.id)
