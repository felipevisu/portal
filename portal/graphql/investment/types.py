from decimal import Decimal

import graphene

from ...investment import models
from ..channel.dataloaders import ChannelByIdLoader
from ..channel.types import Channel
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
    channel = graphene.Field(Channel)
    total = graphene.Decimal()

    class Meta:
        model = models.Investment
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_items(root, info):
        return ItemsByInvestmentIdLoader(info.context).load(root.id)

    @staticmethod
    def resolve_total(root, info):
        def _resolve(items):
            total = sum([Decimal(item.value) for item in items])
            return total if total else Decimal(0.0)

        return ItemsByInvestmentIdLoader(info.context).load(root.id).then(_resolve)

    @staticmethod
    def resolve_channel(root, info):
        if root.channel_id:
            return ChannelByIdLoader(info.context).load(root.channel_id)


class InvestmentCountableConnection(CountableConnection):
    class Meta:
        node = Investment
