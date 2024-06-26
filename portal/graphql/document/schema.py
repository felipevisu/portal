import graphene

from ...core.permissions import DocumentPermissions
from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField, PermissionsField
from .filters import DocumentFilterInput
from .mutations import (
    ApproveDocumentFile,
    DocumentBulkDelete,
    DocumentCreate,
    DocumentDelete,
    DocumentFileDelete,
    DocumentUpdate,
    DocumentUpdateByEntry,
    LoadNewDocumentFromAPI,
    RefuseDocumentFile,
    RequestNewDocument,
    RestoreDocumentFile,
    ValidateDocumentToken,
)
from .resolvers import resolve_document, resolve_document_load, resolve_documents
from .sorters import DocumentSortingInput
from .types import Document, DocumentCountableConnection, DocumentLoad


class Query(graphene.ObjectType):
    document = graphene.Field(Document, id=graphene.Argument(graphene.ID))
    documents = FilterConnectionField(
        DocumentCountableConnection,
        sort_by=DocumentSortingInput(),
        filter=DocumentFilterInput(),
    )
    document_load = PermissionsField(
        DocumentLoad,
        id=graphene.Argument(graphene.ID),
        permissions=[DocumentPermissions.MANAGE_DOCUMENTS],
    )

    def resolve_documents(self, info, **kwargs):
        qs = resolve_documents(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, DocumentCountableConnection)

    def resolve_document(self, info, id=None):
        return resolve_document(info, id)

    def resolve_document_load(self, info, id=None):
        return resolve_document_load(info, id)


class Mutation(graphene.ObjectType):
    document_create = DocumentCreate.Field()
    document_update = DocumentUpdate.Field()
    document_delete = DocumentDelete.Field()
    document_bulk_delete = DocumentBulkDelete.Field()
    document_file_delete = DocumentFileDelete.Field()
    document_update_by_entry = DocumentUpdateByEntry.Field()
    load_new_document_from_API = LoadNewDocumentFromAPI.Field()
    request_new_document = RequestNewDocument.Field()
    validate_token = ValidateDocumentToken.Field()
    approve_document_file = ApproveDocumentFile.Field()
    refuse_document_file = RefuseDocumentFile.Field()
    restore_document_file = RestoreDocumentFile.Field()
