import graphene

from ....attribute import models as models
from ....core.permissions import AttributePermissions
from ...core.mutations import ModelDeleteMutation
from ..types import Attribute


class AttributeDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=False)
        external_reference = graphene.String(required=False)

    class Meta:
        model = models.Attribute
        object_type = Attribute
        permissions = (AttributePermissions.MANAGE_ATTRIBUTES,)
