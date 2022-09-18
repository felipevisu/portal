import graphene

from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField
from .filters import InvestmentFilterInput
from .mutations import (
    InvestmentBulkDelete, InvestmentCreate, InvestmentDelete, InvestmentUpdate,
    ItemBulkCreate, ItemCreate, ItemDelete, ItemUpdate)
from .resolvers import resolve_investment, resolve_investments
from .sorters import InvestmentSortingInput
from .types import Investment, InvestmentCountableConnection


class Query(graphene.ObjectType):
    investment = graphene.Field(
        Investment,
        id=graphene.Argument(graphene.ID),
        month=graphene.Int(),
        year=graphene.Int(),
    )
    investments = FilterConnectionField(
        InvestmentCountableConnection, 
        sort_by=InvestmentSortingInput(), 
        filter=InvestmentFilterInput()
    )

    def resolve_investments(self, info, **kwargs):
        qs = resolve_investments(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, InvestmentCountableConnection)

    def resolve_investment(self, info, id=None, month=None, year=None):
        return resolve_investment(info, id, month, year)


class Mutation(graphene.ObjectType):
    investment_create = InvestmentCreate.Field()
    investment_update = InvestmentUpdate.Field()
    investment_delete = InvestmentDelete.Field()
    investment_bulk_delete = InvestmentBulkDelete.Field()
    item_create = ItemCreate.Field()
    item_bulk_create = ItemBulkCreate.Field()
    item_update = ItemUpdate.Field()
    item_delete = ItemDelete.Field()
