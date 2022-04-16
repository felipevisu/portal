from collections import defaultdict

from ...vehicle.models import Category, Vehicle
from ..core.dataloaders import DataLoader


class CategoryByIdLoader(DataLoader):
    context_key = "category_by_id"

    def batch_load(self, keys):
        categories = Category.objects.in_bulk(keys)
        return [categories.get(category_id) for category_id in keys]


class VehiclesByCategoryIdLoader(DataLoader):
    context_key = "vehicles_by_category_id"

    def batch_load(self, keys):
        vehicles_by_category_ids = defaultdict(list)
        for vehicle in Vehicle.objects.filter(category_id__in=keys).iterator():
            vehicles_by_category_ids[vehicle.category_id].append(vehicle)
        return [vehicles_by_category_ids.get(key, []) for key in keys]
