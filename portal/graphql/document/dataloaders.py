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


class DocumentsByVehicleIdLoader(DataLoader):
    context_key = "documents_by_vehicle_id"

    def batch_load(self, keys):
        documents_by_vehicle_ids = defaultdict(list)
        for document in Document.objects.filter(vehicle_id__in=keys).iterator():
            documents_by_vehicle_ids[document.vehicle_id].append(document)
        return [documents_by_vehicle_ids.get(key, []) for key in keys]
