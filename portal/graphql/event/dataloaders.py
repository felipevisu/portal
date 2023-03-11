from collections import defaultdict

from ...event.models import Event
from ..core.dataloaders import DataLoader


class EventsByDocumentIdLoader(DataLoader):
    context_key = "events_by_document_id"

    def batch_load(self, keys):
        events_by_document_ids = defaultdict(list)
        for event in Event.objects.filter(document_id__in=keys).iterator():
            events_by_document_ids[event.document_id].append(event)
        return [events_by_document_ids.get(key, []) for key in keys]
