import graphene

from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ...core.mutations import ModelDeleteMutation
from ..types import Attribute, AttributeValue


class AttributeValueDelete(ModelDeleteMutation):
    attribute = graphene.Field(Attribute)

    class Arguments:
        id = graphene.ID(required=False)

    class Meta:
        model = models.AttributeValue
        object_type = AttributeValue
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)

    @classmethod
    def success_response(cls, instance):
        response = super().success_response(instance)
        response.attribute = instance.attribute
        return response
