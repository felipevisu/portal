from django.db.models.expressions import Exists, OuterRef

from ..entry.models import Entry
from .models import AssignedEntryAttributeValue, AttributeValue


def associate_attribute_values_to_instance(instance, attribute, *values):
    values_ids = {value.pk for value in values}
    validate_attribute_owns_values(attribute, values_ids)
    return _associate_attribute_to_instance(instance, attribute, *values)


def validate_attribute_owns_values(attribute, value_ids) -> None:
    attribute_actual_value_ids = set(
        AttributeValue.objects.filter(
            pk__in=value_ids, attribute=attribute
        ).values_list("pk", flat=True)
    )
    if attribute_actual_value_ids != value_ids:
        raise AssertionError("Some values are not from the provided attribute.")


def _associate_attribute_to_instance(instance, attribute, *values):
    if isinstance(instance, Entry):
        value_ids = [value.pk for value in values]

        values_qs = AttributeValue.objects.filter(attribute_id=attribute.pk)
        AssignedEntryAttributeValue.objects.filter(
            Exists(values_qs.filter(id=OuterRef("value_id"))),
            entry_id=instance.pk,
        ).exclude(value_id__in=value_ids).delete()

        existing_entry_values = AssignedEntryAttributeValue.objects.filter(
            entry=instance, value_id__in=value_ids
        ).values_list("value_id", flat=True)
        new_values = list(set(value_ids) - set(existing_entry_values))

        AssignedEntryAttributeValue.objects.bulk_create(
            AssignedEntryAttributeValue(entry=instance, value_id=value_id)
            for value_id in new_values
        )

        return None

    raise AssertionError(f"{instance.__class__.__name__} is unsupported")
