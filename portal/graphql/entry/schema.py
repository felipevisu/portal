import graphene

from portal.graphql.core.connection import (
    create_connection_slice,
    filter_connection_queryset,
)

from ..core.fields import FilterConnectionField
from .filters import CategoryFilterInput, EntryFilterInput
from .mutations import (
    CategoryBulkDelete,
    CategoryCreate,
    CategoryDelete,
    CategoryUpdate,
    EntryBulkDelete,
    EntryCreate,
    EntryDelete,
    EntryUpdate,
)
from .resolvers import (
    resolve_categories,
    resolve_category,
    resolve_entries,
    resolve_entry,
)
from .sorters import CategorySortingInput, EntrySortingInput
from .types import (
    Category,
    CategoryCountableConnection,
    Entry,
    EntryCountableConnection,
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
    entry = graphene.Field(
        Entry,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    entries = FilterConnectionField(
        EntryCountableConnection,
        sort_by=EntrySortingInput(),
        filter=EntryFilterInput(),
    )

    def resolve_category(self, info, id=None, slug=None):
        return resolve_category(info, id, slug)

    def resolve_categories(self, info, *args, **kwargs):
        qs = resolve_categories()
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, CategoryCountableConnection)

    def resolve_entry(self, info, id=None, slug=None):
        return resolve_entry(info, id, slug)

    def resolve_entries(self, info, *args, **kwargs):
        qs = resolve_entries(info)
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
