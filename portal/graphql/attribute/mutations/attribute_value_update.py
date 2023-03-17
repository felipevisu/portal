import graphene

from portal.core.permissions import AttributePermissions

from ....attribute import models as models
from ..types import Attribute, AttributeValue
from .attribute_update import AttributeValueUpdateInput
from .attribute_value_create import AttributeValueCreate


class AttributeValueUpdate(AttributeValueCreate):
    attribute = graphene.Field(Attribute)

    class Arguments:
        id = graphene.ID(required=False)
        external_reference = graphene.String(required=False)
        input = AttributeValueUpdateInput(required=True)

    class Meta:
        model = models.AttributeValue
        object_type = AttributeValue
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)

    @classmethod
    def clean_input(cls, info, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if cleaned_input.get("value"):
            cleaned_input["file_url"] = ""
        elif cleaned_input.get("file_url"):
            cleaned_input["value"] = ""
        return cleaned_input

    @classmethod
    def perform_mutation(cls, root, info, /, **data):
        return super(AttributeValueCreate, cls).perform_mutation(root, info, **data)

    @classmethod
    def success_response(cls, instance):
        response = super().success_response(instance)
        response.attribute = instance.attribute
        return response
