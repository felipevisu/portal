import graphene
from django.core.exceptions import ValidationError

from ....attribute import AttributeInputType
from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ....core.utils import generate_unique_slug
from ...core.mutations import ModelMutation
from ..types import Attribute, AttributeValue
from .attribute_create import AttributeValueCreateInput
from .mixins import AttributeMixin
from .validators import validate_value_is_unique


class AttributeValueCreate(AttributeMixin, ModelMutation):
    ATTRIBUTE_VALUES_FIELD = "input"
    attribute = graphene.Field(Attribute)

    class Arguments:
        attribute_id = graphene.ID(required=True, name="attribute")
        input = AttributeValueCreateInput(required=True)

    class Meta:
        model = models.AttributeValue
        object_type = AttributeValue
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)

    @classmethod
    def clean_input(cls, info, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if "name" in cleaned_input:
            cleaned_input["slug"] = generate_unique_slug(
                instance,
                cleaned_input["name"],
                additional_search_lookup={"attribute_id": instance.attribute_id},
            )
        input_type = instance.attribute.input_type

        is_swatch_attr = input_type == AttributeInputType.SWATCH
        errors = {}
        if not is_swatch_attr:
            for field in cls.ONLY_SWATCH_FIELDS:
                if cleaned_input.get(field):
                    errors[field] = [
                        ValidationError(
                            f"The field {field} can be defined only for swatch attributes."
                        )
                    ]
        else:
            try:
                cls.validate_swatch_attr_value(cleaned_input)
            except ValidationError as error:
                errors["value"] = error.error_dict[cls.ATTRIBUTE_VALUES_FIELD]
                errors["fileUrl"] = error.error_dict[cls.ATTRIBUTE_VALUES_FIELD]

        if errors:
            raise ValidationError(errors)

        return cleaned_input

    @classmethod
    def clean_instance(cls, info, instance):
        validate_value_is_unique(instance.attribute, instance)
        super().clean_instance(info, instance)

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info, /, *, attribute_id, input
    ):
        attribute = cls.get_node_or_error(info, attribute_id, only_type=Attribute)
        instance = models.AttributeValue(attribute=attribute)
        cleaned_input = cls.clean_input(info, instance, input)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)

        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
        return AttributeValueCreate(attribute=attribute, attributeValue=instance)
