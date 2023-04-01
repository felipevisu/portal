import graphene
from django.core.exceptions import ValidationError

from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ...core.mutations import ModelMutation
from ...core.types import NonNullList
from ..types import Attribute
from .attribute_create import AttributeValueInput
from .mixins import AttributeMixin


class AttributeValueUpdateInput(AttributeValueInput):
    name = graphene.String(required=False)


class AttributeUpdateInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    remove_values = NonNullList(graphene.ID, name="removeValues")
    add_values = NonNullList(AttributeValueUpdateInput, name="addValues")
    value_required = graphene.Boolean()
    visible_in_website = graphene.Boolean()
    filterable_in_website = graphene.Boolean()
    filterable_in_dashboard = graphene.Boolean()


class AttributeUpdate(AttributeMixin, ModelMutation):
    ATTRIBUTE_VALUES_FIELD = "add_values"

    attribute = graphene.Field(Attribute)

    class Arguments:
        id = graphene.ID(required=False)
        input = AttributeUpdateInput(required=True)

    class Meta:
        model = models.Attribute
        object_type = Attribute
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)

    @classmethod
    def clean_remove_values(cls, cleaned_input, instance):
        remove_values = cleaned_input.get("remove_values", [])
        for value in remove_values:
            if value.attribute != instance:
                msg = f"Value {value} does not belong to this attribute."
                raise ValidationError({"remove_values": ValidationError(msg)})
        return remove_values

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        for attribute_value in cleaned_data.get("remove_values", []):
            attribute_value.delete()

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info, /, *, id=None, input
    ):
        instance = cls.get_instance(info, id=id)

        # Do cleaning and uniqueness checks
        cleaned_input = cls.clean_input(info, instance, input)
        cls.clean_attribute(instance, cleaned_input)
        cls.clean_values(cleaned_input, instance)
        cls.clean_remove_values(cleaned_input, instance)

        # Construct the attribute
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)

        # Commit it
        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
        # Return the attribute that was created
        return AttributeUpdate(attribute=instance)
