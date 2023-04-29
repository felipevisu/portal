from collections import defaultdict

from ...entry.models import Category, Consult, Entry, EntryChannelListing
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
