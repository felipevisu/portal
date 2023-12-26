import graphene

from portal.core.permissions import EntryPermissions
from portal.graphql.channel import ChannelContext

from ....entry import models
from ...attribute.types import SelectedAttribute
from ...channel.types import ChannelContextType
from ...core.connection import CountableConnection, create_connection_slice
from ...core.fields import ConnectionField, PermissionsField
from ...core.types.common import NonNullList
from ...document.dataloaders import DocumentsByEntryIdLoader
from ...document.types import DocumentCountableConnection
from ..dataloaders import (
    CategoriesByEntryIdLoader,
    ConsultByEntryIdLoader,
    EntryChannelListingByEntryIdLoader,
    EntryTypeByIdLoader,
    SelectedAttributesByEntryIdLoader,
)
from ..enums import EntryTypeEnum
from .channels import EntryChannelListing
from .entry_types import EntryType


class Entry(ChannelContextType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    categories = NonNullList("portal.graphql.entry.types.categories.Category")
    document_number = graphene.String()
    email = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)
    type = EntryTypeEnum()
    entry_type = graphene.Field(lambda: EntryType)
    attributes = NonNullList(SelectedAttribute, required=True)
    created = graphene.DateTime()
    updated = graphene.DateTime()
    consult = PermissionsField(
        NonNullList("portal.graphql.entry.types.consults.Consult")
    )
    channel_listings = PermissionsField(
        NonNullList(EntryChannelListing),
        permissions=[EntryPermissions.MANAGE_ENTRIES],
    )
    channel = graphene.String()

    class Meta:
        default_resolver = ChannelContextType.resolver_with_context
        model = models.Entry
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_channel(root: ChannelContext[models.Entry], _info):
        return root.channel_slug

    @staticmethod
    def resolve_categories(root: ChannelContext[models.Entry], info):
        return CategoriesByEntryIdLoader(info.context).load(root.node.id)

    @staticmethod
    def resolve_entry_type(root: ChannelContext[models.Entry], info):
        return EntryTypeByIdLoader(info.context).load(root.node.entry_type_id)

    @staticmethod
    def resolve_documents(root: ChannelContext[models.Entry], info, **kwargs):
        def _resolve(documents):
            return create_connection_slice(
                documents, info, kwargs, DocumentCountableConnection
            )

        return DocumentsByEntryIdLoader(info.context).load(root.node.id).then(_resolve)

    @staticmethod
    def resolve_attributes(root: ChannelContext[models.Entry], info):
        return SelectedAttributesByEntryIdLoader(info.context).load(root.node.id)

    @staticmethod
    def resolve_consult(root: ChannelContext[models.Entry], info, **kwargs):
        return ConsultByEntryIdLoader(info.context).load(root.node.id)

    @staticmethod
    def resolve_channel_listings(root: ChannelContext[models.Entry], info):
        return EntryChannelListingByEntryIdLoader(info.context).load(root.node.id)


class EntryCountableConnection(CountableConnection):
    class Meta:
        node = Entry
