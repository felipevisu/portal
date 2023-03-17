from django.core.exceptions import ValidationError

from ....attribute import models


def validate_value_is_unique(attribute: models.Attribute, value: models.AttributeValue):
    duplicated_values = attribute.values.exclude(pk=value.pk).filter(slug=value.slug)
    if duplicated_values.exists():
        raise ValidationError(
            {"name": ValidationError(f"Value with slug {value.slug} already exists.")}
        )
