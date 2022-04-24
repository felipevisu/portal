import graphene

from ..core.types import SortInputObjectType


class CategorySortField(graphene.Enum):
    NAME = ["name", 'slug']


class CategorySortingInput(SortInputObjectType):
    class Meta:
        sort_enum = CategorySortField
        type_name = "categories"


class VehicleSortField(graphene.Enum):
    NAME = ["name", 'slug']
    UPDATED = ["updated", "name", "slug"]
    CREATED = ["created", "name", "slug"]
    PUBLISHED = ["is_published", "name", "slug"]


class VehicleSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = VehicleSortField
        type_name = "vehicles"
