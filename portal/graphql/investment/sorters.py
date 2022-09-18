import graphene

from ..core.types.sort_input import SortInputObjectType


class InvestmentSortField(graphene.Enum):
    CREATED = ["year", "month"]


class InvestmentSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = InvestmentSortField
        type_name = "investments"
