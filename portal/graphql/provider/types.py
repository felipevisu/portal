import graphene
from graphene_django import DjangoObjectType

from ...provider import models
from ..core.connection import ContableConnection
from ..document.types import DocumentsConnection
from .filters import ProviderFilter, SegmentFilter


class Provider(DjangoObjectType):
    documents = graphene.relay.ConnectionField(DocumentsConnection)

    class Meta:
        model = models.Provider
        filterset_class = ProviderFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_segment(self, info):
        if self.segment_id:
            segment_id = self.segment_id
        else:
            return None
        return info.context.loaders.segment_loader.load(segment_id)

    def resolve_documents(self, info, **kwargs):
        return info.context.loaders.documents_by_provider_loader.load(self.id)


class ProvidersConnection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        node = Provider

    def resolve_total_count(root, info, **kwargs):
        return len(root.edges)


class Segment(DjangoObjectType):
    providers = graphene.relay.ConnectionField(ProvidersConnection)

    class Meta:
        model = models.Segment
        filterset_class = SegmentFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_providers(self, info, **kwargs):
        return info.context.loaders.providers_by_segment_loader.load(self.id)
