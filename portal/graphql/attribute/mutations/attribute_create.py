import graphene

from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ...core.mutations import ModelMutation
from ...core.types import NonNullList
from ..enums import AttributeInputTypeEnum, AttributeTypeEnum
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
    def perform_mutation(cls, _root, info, /, *, input):
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
        # Return the attribute that was created
        return AttributeCreate(attribute=instance)
