import graphene
from django.core.exceptions import ValidationError

from ....attribute import AttributeInputType
from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ...core.mutations import ModelMutation
from ...core.types import NonNullList
from ..enums import AttributeEntityTypeEnum, AttributeInputTypeEnum, AttributeTypeEnum
from ..types import Attribute
from .mixins import AttributeMixin


class AttributeValueInput(graphene.InputObjectType):
    value = graphene.String()
    plain_text = graphene.String()
    file_url = graphene.String(required=False)


class AttributeValueCreateInput(AttributeValueInput):
    name = graphene.String(required=True)


class AttributeCreateInput(graphene.InputObjectType):
    type = AttributeTypeEnum(required=True)
    input_type = AttributeInputTypeEnum()
    entity_type = AttributeEntityTypeEnum()
    name = graphene.String(required=True)
    slug = graphene.String(required=False)
    values = NonNullList(AttributeValueCreateInput)
    value_required = graphene.Boolean()
    visible_in_website = graphene.Boolean()
    filterable_in_website = graphene.Boolean()
    filterable_in_dashboard = graphene.Boolean()


class AttributeCreate(AttributeMixin, ModelMutation):
    ATTRIBUTE_VALUES_FIELD = "values"
    attribute = graphene.Field(Attribute)

    class Arguments:
        input = AttributeCreateInput(required=True)

    class Meta:
        model = models.Attribute
        object_type = Attribute
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)

    @classmethod
    def clean_input(cls, info, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if cleaned_input.get(
            "input_type"
        ) == AttributeInputType.REFERENCE and not cleaned_input.get("entity_type"):
            raise ValidationError(
                {
                    "entity_type": ValidationError(
                        "Entity type is required when REFERENCE input type is used."
                    )
                }
            )
        return cleaned_input

    @classmethod
    def perform_mutation(cls, _root, info, /, *, input):  # type: ignore[override]
        instance = models.Attribute()

        # Do cleaning and uniqueness checks
        cleaned_input = cls.clean_input(info, instance, input)
        cls.clean_attribute(instance, cleaned_input)
        cls.clean_values(cleaned_input, instance)

        # Construct the attribute
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)

        # Commit it
        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
        cls.post_save_action(info, instance, cleaned_input)
        # Return the attribute that was created
        return AttributeCreate(attribute=instance)
