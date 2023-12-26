from collections import defaultdict

from promise import Promise

from ....attribute.models import AssignedEntryAttributeValue, AttributeEntry
from ...attribute.dataloaders import AttributesByAttributeId, AttributeValueByIdLoader
from ...core.dataloaders import DataLoader
from .entries import EntryByIdLoader


class BaseEntryAttributesByEntryTypeIdLoader(DataLoader):
    """Loads entry attributes by entry type ID."""

    model_name = None
    extra_fields = None

    def batch_load(self, keys):
        if not self.model_name:
            raise ValueError("Provide a model_name for this dataloader.")
        if not self.extra_fields:
            self.extra_fields = []

        requestor = self.context.user
        if requestor and requestor.is_active:
            qs = self.model_name.objects.using(self.database_connection_name).all()
        else:
            qs = self.model_name.objects.using(self.database_connection_name).filter(
                attribute__visible_in_website=True
            )

        entry_type_attribute_pairs = qs.filter(entry_type_id__in=keys).values_list(
            "entry_type_id", "attribute_id", *self.extra_fields
        )

        entry_type_to_attributes_map = defaultdict(list)
        for entry_type_id, attr_id, *extra_fields in entry_type_attribute_pairs:
            entry_type_to_attributes_map[entry_type_id].append((attr_id, *extra_fields))

        def map_attributes(attributes):
            attributes_map = {attr.id: attr for attr in attributes}
            return [
                [
                    (attributes_map[attr_id], *extra_fields)
                    for attr_id, *extra_fields in entry_type_to_attributes_map[
                        entry_type_id
                    ]
                ]
                for entry_type_id in keys
            ]

        return (
            AttributesByAttributeId(self.context)
            .load_many(set(attr_id for _, attr_id, *_ in entry_type_attribute_pairs))
            .then(map_attributes)
        )


class EntryAttributesByEntryTypeIdLoader(BaseEntryAttributesByEntryTypeIdLoader):
    """Loads entry attributes by entry type ID."""

    context_key = "entry_attributes_by_entrytype"
    model_name = AttributeEntry


class AttributeValuesByEntryIdLoader(DataLoader):
    context_key = "attributevalues_by_entryid"

    def batch_load(self, keys):
        # Using list + iterator is a small optimisation because iterator causes
        # the db to not store the whole resultset into the memory
        # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#iterator
        attribute_values = list(
            AssignedEntryAttributeValue.objects.using(self.database_connection_name)
            .filter(entry_id__in=keys)
            .iterator()
        )
        value_ids = [a.value_id for a in attribute_values]

        def with_entries(entries):
            entries = [entry for entry in entries if entry]
            entry_type_ids = [p.entry_type_id for p in entries]

            def with_attributes_and_values(result):
                attribute_entries, values = result
                entry_type_attributes = dict(zip(entry_type_ids, attribute_entries))
                values_by_id_map = dict(zip(value_ids, values))
                assigned_entry_map = defaultdict(list)

                for entry in entries:
                    entry_values = [
                        values_by_id_map.get(entry_value.value_id)
                        for entry_value in attribute_values
                        if entry_value.entry_id == entry.id
                    ]

                    attributes = entry_type_attributes[entry.entry_type_id]
                    for attribute_tuple in attributes:
                        attribute = attribute_tuple[0]
                        values = [
                            value
                            for value in entry_values
                            if value and value.attribute_id == attribute.id
                        ]
                        assigned_entry_map[entry.id].append(
                            {
                                "attribute": attribute,
                                "values": values,
                            }
                        )
                return [assigned_entry_map[key] for key in keys]

            attributes = EntryAttributesByEntryTypeIdLoader(self.context).load_many(
                entry_type_ids
            )
            values = AttributeValueByIdLoader(self.context).load_many(value_ids)
            return Promise.all([attributes, values]).then(with_attributes_and_values)

        return EntryByIdLoader(self.context).load_many(keys).then(with_entries)


class SelectedAttributesByEntryIdLoader(DataLoader):
    context_key = "selectedattributes_by_entry"

    def batch_load(self, entry_ids):
        return AttributeValuesByEntryIdLoader(self.context).load_many(entry_ids)
