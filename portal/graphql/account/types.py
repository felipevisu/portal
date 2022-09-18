import graphene
from django.contrib.auth import get_user_model

from ..core.types import ModelObjectType, Permission


class User(ModelObjectType):
    permissions = graphene.List(Permission)

    class Meta:
        model = get_user_model()
        interfaces = [graphene.relay.Node]

    def resolve_permissions(self, info):
        return None
