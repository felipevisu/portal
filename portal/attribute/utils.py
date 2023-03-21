from ..document.models import Document
from ..entry.models import Entry
from .models import AssignedDocumentAttribute, AssignedEntryAttribute


def associate_attribute_values_to_instance(instance, attribute, *values):
    values_ids = {value.pk for value in values}
    validate_attribute_owns_values(attribute, values_ids)
    assignment = _associate_attribute_to_instance(instance, attribute)
    assignment.values.set(values)
    return assignment


def validate_attribute_owns_values(attribute, value_ids) -> None:
    attribute_actual_value_ids = set(attribute.values.values_list("pk", flat=True))
    found_associated_ids = attribute_actual_value_ids & value_ids
    if found_associated_ids != value_ids:
        raise AssertionError("Some values are not from the provided attribute.")


def _associate_attribute_to_instance(instance, attribute):
    if isinstance(instance, Entry):
        assignment, _ = AssignedEntryAttribute.objects.get_or_create(
            entry=instance, attribute=attribute
        )
        return assignment

    if isinstance(instance, Document):
        assignment, _ = AssignedDocumentAttribute.objects.get_or_create(
            document=instance, attribute=attribute
        )

        return assignment

    raise AssertionError(f"{instance.__class__.__name__} is unsupported")
