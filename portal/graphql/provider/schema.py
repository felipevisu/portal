import graphene

from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField
from .filters import ProviderFilterInput, SegmentFilterInput
from .mutations import (
    ProviderBulkDelete,
    ProviderCreate,
    ProviderDelete,
    ProviderUpdate,
    SegmentBulkDelete,
    SegmentCreate,
    SegmentDelete,
    SegmentUpdate,
)
from .resolvers import (
    resolve_provider,
    resolve_providers,
    resolve_segment,
    resolve_segments,
)
from .sorters import ProviderSortingInput, SegmentSortingInput
from .types import (
    Provider,
    ProviderCountableConnection,
    Segment,
    SegmentCountableConnection,
)


class Query(graphene.ObjectType):
    segment = graphene.Field(
        Segment,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    segments = FilterConnectionField(
        SegmentCountableConnection,
        sort_by=SegmentSortingInput(),
        filter=SegmentFilterInput(),
    )
    provider = graphene.Field(
        Provider,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    providers = FilterConnectionField(
        ProviderCountableConnection,
        sort_by=ProviderSortingInput(),
        filter=ProviderFilterInput(),
    )

    def resolve_segments(self, info, *args, **kwargs):
        qs = resolve_segments()
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, SegmentCountableConnection)

    def resolve_segment(self, info, id=None, slug=None):
        return resolve_segment(info, id, slug)

    def resolve_providers(self, info, *args, **kwargs):
        qs = resolve_providers(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, ProviderCountableConnection)

    def resolve_provider(self, info, id=None, slug=None):
        return resolve_provider(info, id, slug)


class Mutation(graphene.ObjectType):
    segment_create = SegmentCreate.Field()
    segment_update = SegmentUpdate.Field()
    segment_delete = SegmentDelete.Field()
    segment_bulk_delete = SegmentBulkDelete.Field()
    provider_create = ProviderCreate.Field()
    provider_update = ProviderUpdate.Field()
    provider_delete = ProviderDelete.Field()
    provider_bulk_delete = ProviderBulkDelete.Field()
