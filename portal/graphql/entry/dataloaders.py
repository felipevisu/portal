from collections import defaultdict

from ...entry.models import Category, Entry
from ..core.dataloaders import DataLoader


class CategoryByIdLoader(DataLoader):
    context_key = "category_by_id"

    def batch_load(self, keys):
        categories = Category.objects.in_bulk(keys)
        return [categories.get(category_id) for category_id in keys]


class EntryByIdLoader(DataLoader):
    context_key = "entry_by_id"

    def batch_load(self, keys):
        entries = Entry.objects.in_bulk(keys)
        return [entries.get(entry_id) for entry_id in keys]


class EntriesByCategoryIdLoader(DataLoader):
    context_key = "entries_by_category_id"

    def batch_load(self, keys):
        entries_by_category_ids = defaultdict(list)
        for entry in (
            Entry.objects.visible_to_user(self.user)
            .using(self.database_connection_name)
            .filter(category_id__in=keys)
            .iterator()
        ):
            entries_by_category_ids[entry.category_id].append(entry)
        return [entries_by_category_ids.get(key, []) for key in keys]
