import graphene

from ....entry import models
from ...core.connection import CountableConnection, create_connection_slice
from ...core.fields import ConnectionField
from ...core.types import ModelObjectType
from ..dataloaders import EntriesByCategoryIdLoader
from ..enums import EntryTypeEnum
from .entries import EntryCountableConnection


class Category(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    type = EntryTypeEnum()
    entries = ConnectionField(EntryCountableConnection)
    total_entries = graphene.Int()

    class Meta:
        model = models.Category
        interfaces = [graphene.relay.Node]

    def resolve_entries(self, info, **kwargs):
        def _resolve(entries):
            return create_connection_slice(
                entries, info, kwargs, EntryCountableConnection
            )

        return EntriesByCategoryIdLoader(info.context).load(self.id).then(_resolve)


class CategoryCountableConnection(CountableConnection):
    class Meta:
        node = Category
