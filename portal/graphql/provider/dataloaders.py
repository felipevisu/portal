from collections import defaultdict

from ...provider.models import Document, Provider, Segment
from ..core.dataloaders import DataLoader


class SegmentByIdLoader(DataLoader):
    context_key = "segment_by_id"

    def batch_load(self, keys):
        segments = Segment.objects.in_bulk(keys)
        return [segments.get(segment_id) for segment_id in keys]


class ProvidersBySegmentIdLoader(DataLoader):
    context_key = "providers_by_segment_id"

    def batch_load(self, keys):
        providers_by_segment_ids = defaultdict(list)
        for provider in Provider.objects.filter(segment_id__in=keys).iterator():
            providers_by_segment_ids[provider.segment_id].append(provider)
        return [providers_by_segment_ids.get(key, []) for key in keys]


class DocumentsByProviderIdLoader(DataLoader):
    context_key = "documents_by_provider_id"

    def batch_load(self, keys):
        documents_by_provider_ids = defaultdict(list)
        for document in Document.objects.filter(provider_id__in=keys).iterator():
            documents_by_provider_ids[document.provider_id].append(document)
        return [documents_by_provider_ids.get(key, []) for key in keys]
