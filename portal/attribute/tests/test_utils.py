import pytest

from ...investment.models import Investment
from ..utils import associate_attribute_values_to_instance

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
    old_assignment = provider.attributes.first()
    assert old_assignment is not None, "The entry doesn't have attribute-values"
    assert old_assignment.values.count() == 1

    attribute = old_assignment.attribute

    # Clear the values
    new_assignment = associate_attribute_values_to_instance(provider, attribute)

    # Ensure the values were cleared and no new assignment entry was created
    assert new_assignment.pk == old_assignment.pk
    assert new_assignment.values.count() == 0


def test_associate_attribute_to_product_instance_multiple_values(provider):
    """Ensure multiple values in proper order are assigned."""
    old_assignment = provider.attributes.first()
    assert old_assignment is not None, "The entry doesn't have attribute-values"
    assert old_assignment.values.count() == 1

    attribute = old_assignment.attribute
    values = attribute.values.all()

    # Assign new values
    new_assignment = associate_attribute_values_to_instance(
        provider, attribute, values[1], values[0]
    )

    # Ensure the new assignment was created and ordered correctly
    assert new_assignment.pk == old_assignment.pk
    assert new_assignment.values.count() == 2
