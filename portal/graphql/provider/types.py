import graphene

from portal.graphql.document.dataloaders import DocumentsByProviderIdLoader

from ...provider import models
from ..core.connection import CountableConnection, create_connection_slice
from ..core.fields import ConnectionField
from ..core.types import ModelObjectType
from ..document.types import DocumentCountableConnection
from .dataloaders import ProvidersBySegmentIdLoader, SegmentByIdLoader


class Provider(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    segment = graphene.Field(lambda: Segment)
    document_number = graphene.String()
    is_published = graphene.Boolean()
    email = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)

    class Meta:
        model = models.Provider
        interfaces = [graphene.relay.Node]

    def resolve_segment(self, info):
        if self.segment_id:
            segment_id = self.segment_id
        else:
            return None
        return SegmentByIdLoader(info.context).load(segment_id)

    def resolve_documents(self, info, **kwargs):
        def _resolve(documents):
            return create_connection_slice(
                documents, info, kwargs, DocumentCountableConnection
            )

        return DocumentsByProviderIdLoader(info.context).load(self.id).then(_resolve)


class ProviderCountableConnection(CountableConnection):
    class Meta:
        node = Provider


class Segment(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    providers = ConnectionField(ProviderCountableConnection)

    class Meta:
        model = models.Segment
        interfaces = [graphene.relay.Node]

    def resolve_providers(self, info, **kwargs):
        def _resolve(providers):
            create_connection_slice(
                providers, info, kwargs, ProviderCountableConnection
            )

        return ProvidersBySegmentIdLoader(info.context).load(self.id).then(_resolve)


class SegmentCountableConnection(CountableConnection):
    class Meta:
        node = Segment
