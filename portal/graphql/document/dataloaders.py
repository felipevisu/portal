from collections import defaultdict

from ...document.models import Document
from ..core.dataloaders import DataLoader


class DocumentsByProviderIdLoader(DataLoader):
    context_key = "documents_by_provider_id"

    def batch_load(self, keys):
        documents_by_provider_ids = defaultdict(list)
        for document in Document.objects.filter(provider_id__in=keys).iterator():
            documents_by_provider_ids[document.provider_id].append(document)
        return [documents_by_provider_ids.get(key, []) for key in keys]


class DocumentsByEntryIdLoader(DataLoader):
    context_key = "documents_by_entry_id"

    def batch_load(self, keys):
        documents_by_entry_ids = defaultdict(list)
        for document in Document.objects.filter(entry_id__in=keys).iterator():
            documents_by_entry_ids[document.entry_id].append(document)
        return [documents_by_entry_ids.get(key, []) for key in keys]
