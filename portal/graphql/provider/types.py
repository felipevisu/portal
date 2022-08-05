import graphene
from graphene_django import DjangoObjectType

from portal.graphql.core.connection import ContableConnection
from portal.graphql.provider.dataloaders import (
    ProvidersBySegmentIdLoader, SegmentByIdLoader)
from portal.graphql.provider.filters import (
    DocumentFilter, ProviderFilter, SegmentFilter)
from portal.provider import models

segment_loader = SegmentByIdLoader()
providers_loader = ProvidersBySegmentIdLoader()


class Document(DjangoObjectType):
    file_url = graphene.String()
    file_name = graphene.String()

    class Meta:
        model = models.Document
        filterset_class = DocumentFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_file_url(self, info):
        return self.file.url

    def resolve_file_name(self, info):
        return self.file.name.split('/')[-1]


class DocumentsConnection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        node = Document

    def resolve_total_count(root, info, **kwargs):
        return len(root.edges)


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
        return segment_loader.load(segment_id)

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
        return providers_loader.load(self.id)
