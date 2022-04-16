import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .mutations import (
    DocumentCreate,
    DocumentDelete,
    DocumentUpdate,
    ProviderCreate,
    ProviderDelete,
    ProviderUpdate,
    SegmentCreate,
    SegmentDelete,
    SegmentUpdate,
)
from .resolvers import (
    resolve_document,
    resolve_documents,
    resolve_provider,
    resolve_providers,
    resolve_segment,
)
from .types import Document, Provider, Segment


class Query(graphene.ObjectType):
    segment = graphene.Field(
        Segment,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    segments = DjangoFilterConnectionField(Segment)
    provider = graphene.Field(
        Provider,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    providers = DjangoFilterConnectionField(Provider)
    document = graphene.Field(
        Document,
        id=graphene.Argument(graphene.ID)
    )
    documents = DjangoFilterConnectionField(Document)

    def resolve_segment(self, info, id=None, slug=None):
        return resolve_segment(info, id, slug)

    def resolve_providers(self, info, *args, **kwargs):
        return resolve_providers(info)

    def resolve_provider(self, info, id=None, slug=None):
        return resolve_provider(info, id, slug)

    def resolve_documents(self, info, *args, **kwargs):
        return resolve_documents(info)

    def resolve_document(self, info, id=None):
        return resolve_document(info, id)


class Mutation(graphene.ObjectType):
    segment_create = SegmentCreate.Field()
    segment_update = SegmentUpdate.Field()
    segment_delete = SegmentDelete.Field()
    provider_create = ProviderCreate.Field()
    provider_update = ProviderUpdate.Field()
    provider_delete = ProviderDelete.Field()
    document_create = DocumentCreate.Field()
    document_update = DocumentUpdate.Field()
    document_delete = DocumentDelete.Field()
