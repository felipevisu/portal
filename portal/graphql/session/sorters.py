import graphene

from ..core.types.sort_input import SortInputObjectType


class SessionSortField(graphene.Enum):
    NAME = ["name"]


class SessionSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = SessionSortField
        type_name = "sessions"
