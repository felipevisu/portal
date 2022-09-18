import graphene

from ...provider import models
from ..core.connection import CountableConnection, create_connection_slice
from ..core.fields import ConnectionField
from ..core.types import ModelObjectType
from ..document.types import DocumentCountableConnection
from .dataloaders import SegmentByIdLoader


class Provider(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    segment = graphene.Field(lambda: Segment)
    document_number = graphene.String()
    is_published = graphene.String()
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
        qs = self.documents.all()
        return create_connection_slice(qs, info, kwargs, DocumentCountableConnection)


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
        qs = self.providers.all()
        return create_connection_slice(qs, info, kwargs, ProviderCountableConnection)

class SegmentCountableConnection(CountableConnection):
    class Meta:
        node = Segment
