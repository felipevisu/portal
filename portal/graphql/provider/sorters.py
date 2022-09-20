import graphene

from ..core.types import SortInputObjectType


class SegmentSortField(graphene.Enum):
    NAME = ["name", "slug"]


class SegmentSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = SegmentSortField
        type_name = "segments"


class ProviderSortField(graphene.Enum):
    NAME = ["name", "slug"]
    UPDATED = ["updated", "name", "slug"]
    CREATED = ["created", "name", "slug"]
    PUBLISHED = ["is_published", "name", "slug"]


class ProviderSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = ProviderSortField
        type_name = "providers"
