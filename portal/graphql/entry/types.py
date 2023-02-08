import graphene

from portal.graphql.document.dataloaders import DocumentsByEntryIdLoader
from portal.graphql.entry.enums import EntryTypeEnum

from ...entry import models
from ..core.connection import CountableConnection, create_connection_slice
from ..core.fields import ConnectionField
from ..core.types import ModelObjectType
from ..document.types import DocumentCountableConnection
from .dataloaders import CategoryByIdLoader, EntriesByCategoryIdLoader
from .enums import EntryTypeEnum


class Entry(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    category = graphene.Field(lambda: Category)
    document_number = graphene.String()
    is_published = graphene.Boolean()
    email = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)
    type = EntryTypeEnum()

    class Meta:
        model = models.Entry
        interfaces = [graphene.relay.Node]

    def resolve_documents(self, info, **kwargs):
        def _resolve(documents):
            return create_connection_slice(
                documents, info, kwargs, DocumentCountableConnection
            )

        return DocumentsByEntryIdLoader(info.context).load(self.id).then(_resolve)

    def resolve_category(self, info):
        if self.category_id:
            category_id = self.category_id
        else:
            return None
        return CategoryByIdLoader(info.context).load(category_id)


class EntryCountableConnection(CountableConnection):
    class Meta:
        node = Entry


class Category(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
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
