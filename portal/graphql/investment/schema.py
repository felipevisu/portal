import graphene
from graphene_django.filter import DjangoFilterConnectionField

from portal.graphql.investment.mutations import (
    InvestmentCreate,
    InvestmentDelete,
    InvestmentUpdate,
    ItemBulkCreate,
    ItemCreate,
    ItemDelete,
    ItemUpdate,
)

from .resolvers import resolve_investment, resolve_investments
from .types import Investment


class Query(graphene.ObjectType):
    investment = graphene.Field(
        Investment,
        id=graphene.Argument(graphene.ID),
        mounth=graphene.Int(),
        year=graphene.Int(),
    )
    investments = DjangoFilterConnectionField(Investment)

    def resolve_investments(self, info, *args, **kwargs):
        return resolve_investments(info)

    def resolve_investment(self, info, id=None, mounth=None, year=None):
        return resolve_investment(info, id, mounth, year)


class Mutation(graphene.ObjectType):
    investment_create = InvestmentCreate.Field()
    investment_update = InvestmentUpdate.Field()
    investment_delete = InvestmentDelete.Field()
    item_create = ItemCreate.Field()
    item_bulk_create = ItemBulkCreate.Field()
    item_update = ItemUpdate.Field()
    item_delete = ItemDelete.Field()
