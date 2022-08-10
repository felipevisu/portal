import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .mutations import DocumentCreate, DocumentDelete, DocumentUpdate
from .resolvers import resolve_document, resolve_documents
from .types import Document


class Query(graphene.ObjectType):
    document = graphene.Field(
        Document,
        id=graphene.Argument(graphene.ID)
    )
    documents = DjangoFilterConnectionField(Document)

    def resolve_documents(self, info, *args, **kwargs):
        return resolve_documents(info)

    def resolve_document(self, info, id=None):
        return resolve_document(info, id)


class Mutation(graphene.ObjectType):
    document_create = DocumentCreate.Field()
    document_update = DocumentUpdate.Field()
    document_delete = DocumentDelete.Field()
