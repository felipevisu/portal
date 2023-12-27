import pytest

from ...investment.models import Investment
from ..utils import associate_attribute_values_to_instance
from .model_helper import get_entry_attribute_values, get_entry_attributes

pytestmark = pytest.mark.django_db


def test_associate_attribute_to_non_entry_instance(color_attribute):
    instance = Investment()
    attribute = color_attribute
    value = color_attribute.values.first()

    with pytest.raises(AssertionError) as exc:
        associate_attribute_values_to_instance(instance, attribute, value)

    assert exc.value.args == ("Investment is unsupported",)


def test_associate_attribute_to_entry_instance_from_different_attribute(
    provider, color_attribute, size_attribute
):
    """Ensure an assertion error is raised when one tries to associate attribute values
    to an object that don't belong to the supplied attribute.
    """
    instance = provider
    attribute = color_attribute
    value = size_attribute.values.first()

    with pytest.raises(AssertionError) as exc:
        associate_attribute_values_to_instance(instance, attribute, value)

    assert exc.value.args == ("Some values are not from the provided attribute.",)


def test_associate_attribute_to_entry_instance_without_values(provider):
    """Ensure clearing the values from a entry is properly working."""
    attribute = get_entry_attributes(provider).first()
    assert attribute is not None, "Entry doesn't have attributes assigned"
    value_count = get_entry_attribute_values(provider, attribute).count()
    assert value_count == 1, "Entry doesn't have attribute-values"

    # Clear the values
    associate_attribute_values_to_instance(provider, attribute)

    # Ensure the values were cleared and no new assignment entry was created
    assert get_entry_attributes(provider).count() == 1
    assert provider.attributevalues.count() == 0


def test_associate_attribute_to_entry_instance_multiple_values(
    provider, attribute_value_generator
):
    attribute = get_entry_attributes(provider).first()
    assert attribute is not None, "Product doesn't have attributes assigned"
    value_count = get_entry_attribute_values(provider, attribute).count()
    assert value_count == 1, "Product doesn't have attribute-values"

    attribute_value_generator(
        attribute=attribute,
        slug="attr-value2",
    )
    values = attribute.values.all()

    # Assign new values
    associate_attribute_values_to_instance(provider, attribute, values[1], values[0])

    # Ensure the new assignment was created and ordered correctly
    assert provider.attributevalues.count() == 2
