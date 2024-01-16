import graphene

from ....attribute import models as attribute_models
from ....core.db.utils import get_database_connection_name
from ....core.permissions import EntryPermissions
from ....entry import models
from ...attribute.filters import AttributeFilterInput
from ...attribute.resolvers import resolve_attributes
from ...attribute.types import (
    Attribute,
    AttributeCountableConnection,
    SelectedAttribute,
)
from ...channel import ChannelContext
from ...channel.types import ChannelContextType
from ...core.connection import (
    CountableConnection,
    create_connection_slice,
    filter_connection_queryset,
)
from ...core.fields import ConnectionField, FilterConnectionField, PermissionsField
from ...core.types import ModelObjectType
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
from ..dataloaders.attributes import EntryAttributesByEntryTypeIdLoader
from .channels import EntryChannelListing


class EntryType(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    entry_attributes = NonNullList(
        Attribute, description="Product attributes of that product type."
    )
    available_attributes = FilterConnectionField(
        AttributeCountableConnection,
        filter=AttributeFilterInput(),
        description="List of attributes which can be assigned to this product type.",
        permissions=[EntryPermissions.MANAGE_ENTRY_TYPES],
    )

    class Meta:
        model = models.EntryType
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_entry_attributes(root: models.EntryType, info):
        def unpack_attributes(attributes):
            return [attr for attr, *_ in attributes]

        return (
            EntryAttributesByEntryTypeIdLoader(info.context)
            .load(root.pk)
            .then(unpack_attributes)
        )

    @staticmethod
    def resolve_available_attributes(root: models.EntryType, info, **kwargs):
        qs = attribute_models.Attribute.objects.get_unassigned_entry_type_attributes(
            root.pk
        ).using(get_database_connection_name(info.context))
        qs = resolve_attributes(info, qs=qs)
        qs = filter_connection_queryset(qs, kwargs, info.context)
        return create_connection_slice(qs, info, kwargs, AttributeCountableConnection)


class EntryTypeCountableConnection(CountableConnection):
    class Meta:
        node = EntryType


class Entry(ChannelContextType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    categories = NonNullList("portal.graphql.entry.types.categories.Category")
    document_number = graphene.String()
    email = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)
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
