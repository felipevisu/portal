import graphene

from ..core.types import SortInputObjectType


class CategorySortField(graphene.Enum):
    NAME = ["name", "slug"]


class CategorySortingInput(SortInputObjectType):
    class Meta:
        sort_enum = CategorySortField
        type_name = "categories"


class EntrySortField(graphene.Enum):
    NAME = ["name", "slug"]
    UPDATED = ["updated", "name", "slug"]
    CREATED = ["created", "name", "slug"]
    PUBLISHED = ["is_published", "name", "slug"]


class EntrySortingInput(SortInputObjectType):
    class Meta:
        sort_enum = EntrySortField
        type_name = "entries"
