import graphene

from portal.graphql.channel import ChannelContext
from portal.graphql.core.connection import (
    create_connection_slice,
    filter_connection_queryset,
)

from ..channel.utils import get_default_channel_slug_or_graphql_error
from ..core.fields import BaseField, FilterConnectionField
from .filters import CategoryFilterInput, EntryFilterInput
from .mutations import (
    CategoryBulkDelete,
    CategoryCreate,
    CategoryDelete,
    CategoryUpdate,
    ConsultDocument,
    EntryAttributeAssign,
    EntryAttributeUnassign,
    EntryBulkDelete,
    EntryChannelListingUpdate,
    EntryCreate,
    EntryDelete,
    EntryTypeCreate,
    EntryTypeDelete,
    EntryTypeUpdate,
    EntryUpdate,
)
from .resolvers import (
    resolve_categories,
    resolve_category,
    resolve_entries,
    resolve_entry,
    resolve_entry_type,
    resolve_entry_types,
)
from .sorters import CategorySortingInput, EntrySortingInput, EntryTypeSortingInput
from .types import (
    Category,
    CategoryCountableConnection,
    Entry,
    EntryCountableConnection,
    EntryType,
    EntryTypeCountableConnection,
)


class Query(graphene.ObjectType):
    category = graphene.Field(
        Category,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    categories = FilterConnectionField(
        CategoryCountableConnection,
        sort_by=CategorySortingInput(),
        filter=CategoryFilterInput(),
    )
    entry = BaseField(
        Entry,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
        channel=graphene.String(),
    )
    entries = FilterConnectionField(
        EntryCountableConnection,
        sort_by=EntrySortingInput(),
        filter=EntryFilterInput(),
        channel=graphene.String(),
    )
    entry_type = BaseField(
        EntryType,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    entry_types = FilterConnectionField(
        EntryTypeCountableConnection,
        sort_by=EntryTypeSortingInput(),
    )

    def resolve_category(self, info, id=None, slug=None):
        return resolve_category(info, id, slug)

    def resolve_categories(self, info, *args, **kwargs):
        qs = resolve_categories()
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, CategoryCountableConnection)

    def resolve_entry_type(self, info, id=None, slug=None):
        return resolve_entry_type(info, id, slug)

    def resolve_entry_types(self, info, *args, **kwargs):
        qs = resolve_entry_types()
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, EntryTypeCountableConnection)

    def resolve_entry(
        self,
        info,
        *,
        id=None,
        slug=None,
        channel=None,
    ):
        if channel is None and not info.context.user:
            channel = get_default_channel_slug_or_graphql_error()
        entry = resolve_entry(info, id, slug, channel_slug=channel)
        return ChannelContext(node=entry, channel_slug=channel) if entry else None

    def resolve_entries(self, info, *, channel=None, **kwargs):
        if channel is None and not info.context.user:
            channel = get_default_channel_slug_or_graphql_error()
        qs = resolve_entries(info, channel_slug=channel)
        kwargs["channel"] = channel
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, EntryCountableConnection)


class Mutation(graphene.ObjectType):
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    category_bulk_delete = CategoryBulkDelete.Field()
    entry_create = EntryCreate.Field()
    entry_update = EntryUpdate.Field()
    entry_delete = EntryDelete.Field()
    entry_bulk_delete = EntryBulkDelete.Field()
    entry_channel_listing_update = EntryChannelListingUpdate.Field()
    consult_document = ConsultDocument.Field()
    entry_type_create = EntryTypeCreate.Field()
    entry_type_update = EntryTypeUpdate.Field()
    entry_type_delete = EntryTypeDelete.Field()
    entry_attribute_assign = EntryAttributeAssign.Field()
    entry_attribute_unassign = EntryAttributeUnassign.Field()
