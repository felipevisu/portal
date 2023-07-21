from collections import defaultdict

from ...document.models import Document, DocumentFile
from ..core.dataloaders import DataLoader


class DocumentByIdLoader(DataLoader):
    context_key = "document_by_id"

    def batch_load(self, keys):
        documents = Document.objects.in_bulk(keys)
        return [documents.get(document_id) for document_id in keys]


class DocumentsByEntryIdLoader(DataLoader):
    context_key = "documents_by_entry_id"

    def batch_load(self, keys):
        documents_by_entry_ids = defaultdict(list)
        for document in (
            Document.objects.visible_to_user(self.user)
            .filter(entry_id__in=keys)
            .iterator()
        ):
            documents_by_entry_ids[document.entry_id].append(document)
        return [documents_by_entry_ids.get(key, []) for key in keys]


class DocumentFileByIdLoader(DataLoader):
    context_key = "document_file_by_id"

    def batch_load(self, keys):
        document_files = DocumentFile.objects.in_bulk(keys)
        return [document_files.get(document_file_id) for document_file_id in keys]


class DocumentFilesByDocumentIdLoader(DataLoader):
    context_key = "document_files_by_document_id"

    def batch_load(self, keys):
        documents_files_by_document_id = defaultdict(list)
        for document_file in DocumentFile.objects.filter(
            document_id__in=keys
        ).iterator():
            documents_files_by_document_id[document_file.document_id].append(
                document_file
            )
        return [documents_files_by_document_id.get(key, []) for key in keys]
