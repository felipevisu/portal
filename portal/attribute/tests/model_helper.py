from django.db.models.expressions import Exists, OuterRef

from ..models import (
    AssignedEntryAttributeValue,
    Attribute,
    AttributeEntry,
    AttributeValue,
)


def get_entry_attributes(entry):
    """Get entry attributes filtered by entry_type.

    ProductType defines which attributes can be assigned to a entry and
    we have to filter out the attributes on the instance by the ones attached to the
    entry_type.
    """
    entry_attributes = AttributeEntry.objects.filter(entry_type_id=entry.entry_type_id)
    return Attribute.objects.filter(
        Exists(entry_attributes.filter(attribute_id=OuterRef("id")))
    ).order_by("pk")


def get_entry_attribute_values(entry, attribute):
    """Get values assigned to a entry.

    Note: this doesn't filter out attributes that might have been unassigned from the
    entry type.
    """
    assigned_values = AssignedEntryAttributeValue.objects.filter(entry_id=entry.pk)

    return AttributeValue.objects.filter(
        Exists(
            assigned_values.filter(value_id=OuterRef("id")),
        ),
        attribute_id=attribute.pk,
    ).order_by("pk")
