from collections import defaultdict

from promise import Promise

from portal.graphql.entry.dataloaders import EntryByIdLoader

from ...attribute.models import (
    AssignedEntryAttribute,
    AssignedEntryAttributeValue,
    Attribute,
    AttributeValue,
)
from ..core.dataloaders import DataLoader


class AttributesByAttributeId(DataLoader):
    context_key = "attributes_by_id"

    def batch_load(self, keys):
        attributes = Attribute.objects.using(self.database_connection_name).in_bulk(
            keys
        )
        return [attributes.get(key) for key in keys]


class AttributeValueByIdLoader(DataLoader):
    context_key = "attributevalue_by_id"

    def batch_load(self, keys):
        attribute_values = AttributeValue.objects.using(
            self.database_connection_name
        ).in_bulk(keys)
        return [attribute_values.get(attribute_value_id) for attribute_value_id in keys]


class AssignedEntryAttributesByEntryIdLoader(DataLoader):
    context_key = "assignedentryattributes_by_entry"

    def batch_load(self, keys):
        user = self.context.user
        if user and user.is_staff:
            qs = AssignedEntryAttribute.objects.using(
                self.database_connection_name
            ).all()
        else:
            qs = AssignedEntryAttribute.objects.using(
                self.database_connection_name
            ).filter(attribute__visible_in_website=True)
        assigned_entry_attributes = qs.filter(entry_id__in=keys)
        entry_to_assignedentryattributes = defaultdict(list)
        for assigned_entry_attribute in assigned_entry_attributes.iterator():
            entry_to_assignedentryattributes[assigned_entry_attribute.entry_id].append(
                assigned_entry_attribute
            )
        return [entry_to_assignedentryattributes[entry_id] for entry_id in keys]


class AttributeValuesByAssignedEntryAttributeIdLoader(DataLoader):
    context_key = "attributevalues_by_assignedentryattribute"

    def batch_load(self, keys):
        attribute_values = list(
            AssignedEntryAttributeValue.objects.using(self.database_connection_name)
            .filter(assignment_id__in=keys)
            .iterator()
        )
        value_ids = [a.value_id for a in attribute_values]

        def map_assignment_to_values(values):
            value_map = dict(zip(value_ids, values))
            assigned_entry_map = defaultdict(list)
            for attribute_value in attribute_values:
                assigned_entry_map[attribute_value.assignment_id].append(
                    value_map.get(attribute_value.value_id)
                )
            return [assigned_entry_map[key] for key in keys]

        return (
            AttributeValueByIdLoader(self.context)
            .load_many(value_ids)
            .then(map_assignment_to_values)
        )


class SelectedAttributesByEntryIdLoader(DataLoader):
    context_key = "selectedattributes_by_entry"

    def batch_load(self, keys):
        def with_entries_and_assigned_attributes(result):
            entries, assigned_entry_attributes = result
            attribute_ids = [
                attr.attribute_id for item in assigned_entry_attributes for attr in item
            ]
            entries = [entry for entry in entries if entry is not None]
            assigned_entry_attributes_ids = [
                a.id for attrs in assigned_entry_attributes for a in attrs
            ]
            assigned_entry_attributes = dict(zip(keys, assigned_entry_attributes))

            def with_attribute_and_values(result):
                attributes, attribute_values = result
                attributes = dict(zip(assigned_entry_attributes_ids, attributes))
                attribute_values = dict(
                    zip(assigned_entry_attributes_ids, attribute_values)
                )
                selected_attributes_map = defaultdict(list)
                for key in keys:
                    assigneds = assigned_entry_attributes[key]
                    for assigned in assigneds:
                        values = attribute_values[assigned.id] or []
                        attribute = attributes[assigned.id]
                        selected_attributes_map[key].append(
                            {"values": values, "attribute": attribute}
                        )

                return [selected_attributes_map[key] for key in keys]

            attributes = AttributesByAttributeId(self.context).load_many(attribute_ids)
            attribute_values = AttributeValuesByAssignedEntryAttributeIdLoader(
                self.context
            ).load_many(assigned_entry_attributes_ids)

            return Promise.all([attributes, attribute_values]).then(
                with_attribute_and_values
            )

        entries = EntryByIdLoader(self.context).load_many(keys)
        assigned_entry_attributes = AssignedEntryAttributesByEntryIdLoader(
            self.context
        ).load_many(keys)

        return Promise.all([entries, assigned_entry_attributes]).then(
            with_entries_and_assigned_attributes
        )
