import graphene

from ..core.types.sort_input import SortInputObjectType


class DocumentSortField(graphene.Enum):
    CREATED = ["created"]


class DocumentSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = DocumentSortField
        type_name = "documents"
