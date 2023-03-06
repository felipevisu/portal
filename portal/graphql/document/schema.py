import graphene

from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField
from .filters import DocumentFilterInput
from .mutations import (
    DocumentBulkDelete,
    DocumentCreate,
    DocumentDelete,
    DocumentUpdate,
    RequestNewDocument,
)
from .resolvers import resolve_document, resolve_documents
from .sorters import DocumentSortingInput
from .types import Document, DocumentCountableConnection


class Query(graphene.ObjectType):
    document = graphene.Field(Document, id=graphene.Argument(graphene.ID))
    documents = FilterConnectionField(
        DocumentCountableConnection,
        sort_by=DocumentSortingInput(),
        filter=DocumentFilterInput(),
    )

    def resolve_documents(self, info, **kwargs):
        qs = resolve_documents(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, DocumentCountableConnection)

    def resolve_document(self, info, id=None):
        return resolve_document(info, id)


class Mutation(graphene.ObjectType):
    document_create = DocumentCreate.Field()
    document_update = DocumentUpdate.Field()
    document_delete = DocumentDelete.Field()
    document_bulk_delete = DocumentBulkDelete.Field()
    request_new_document = RequestNewDocument.Field()
