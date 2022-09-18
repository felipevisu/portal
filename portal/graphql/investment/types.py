import graphene

from ...investment import models
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType, NonNullList
from .dataloaders import ItemsByInvestmentIdLoader


class Item(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    value = graphene.Decimal()
    investment = graphene.Field(lambda: Investment)

    class Meta:
        model = models.Item
        interfaces = [graphene.relay.Node]


class ItemCountableConnection(CountableConnection):
    class Meta:
        node = Item


class Investment(ModelObjectType):
    id = graphene.GlobalID(required=True)
    year = graphene.Int(required=True)
    month = graphene.Int(required=True)
    is_published = graphene.Boolean()
    items = NonNullList(Item)

    class Meta:
        model = models.Investment
        interfaces = [graphene.relay.Node]

    def resolve_items(self, info):
        return ItemsByInvestmentIdLoader(info.context).load(self.id)


class InvestmentCountableConnection(CountableConnection):
    class Meta:
        node = Investment
