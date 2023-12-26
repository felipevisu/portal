from collections import defaultdict

from ....entry.models import (
    Category,
    CategoryEntry,
    Consult,
    Entry,
    EntryChannelListing,
    EntryType,
)
from ...core.dataloaders import DataLoader


class EntryTypeByIdLoader(DataLoader):
    context_key = "entry_type_by_id"

    def batch_load(self, keys):
        entry_types = EntryType.objects.using(self.database_connection_name).in_bulk(
            keys
        )
        return [entry_types.get(entry_type_id) for entry_type_id in keys]


class CategoryByIdLoader(DataLoader):
    context_key = "category_by_id"

    def batch_load(self, keys):
        categories = Category.objects.in_bulk(keys)
        return [categories.get(category_id) for category_id in keys]


class CategoriesByEntryIdLoader(DataLoader):
    context_key = "categoryes_by_entry"

    def batch_load(self, keys):
        entry_category_pairs = list(
            CategoryEntry.objects.using(self.database_connection_name)
            .using(self.database_connection_name)
            .filter(entry_id__in=keys)
            .order_by("id")
            .values_list("entry_id", "category_id")
            .iterator()
        )
        entry_category_map = defaultdict(list)
        for pid, cid in entry_category_pairs:
            entry_category_map[pid].append(cid)

        def map_categories(collections):
            category_map = {c.id: c for c in collections}
            return [
                [category_map[cid] for cid in entry_category_map[pid]] for pid in keys
            ]

        return (
            CategoryByIdLoader(self.context)
            .load_many(set(cid for pid, cid in entry_category_pairs))
            .then(map_categories)
        )


class EntryByIdLoader(DataLoader):
    context_key = "entry_by_id"

    def batch_load(self, keys):
        entries = Entry.objects.in_bulk(keys)
        return [entries.get(entry_id) for entry_id in keys]


class ConsultByEntryIdLoader(DataLoader):
    context_key = "consult_by_entry_id"

    def batch_load(self, keys):
        consult_by_entry_ids = defaultdict(list)
        for consult in (
            Consult.objects.all()
            .using(self.database_connection_name)
            .filter(entry_id__in=keys)
            .iterator()
        ):
            consult_by_entry_ids[consult.entry_id].append(consult)
        return [consult_by_entry_ids.get(key, []) for key in keys]


class EntryChannelListingByEntryIdLoader(DataLoader[int, EntryChannelListing]):
    context_key = "entrychannelisting_by_entry"

    def batch_load(self, keys):
        entry_channel_listings = (
            EntryChannelListing.objects.using(self.database_connection_name)
            .filter(entry_id__in=keys)
            .iterator()
        )
        channel_listings_by_entry_ids = defaultdict(list)
        for channel_listing in entry_channel_listings:
            channel_listings_by_entry_ids[channel_listing.entry_id].append(
                channel_listing
            )
        return [channel_listings_by_entry_ids.get(key, []) for key in keys]
