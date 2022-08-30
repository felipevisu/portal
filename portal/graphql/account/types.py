import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from ..core.types import Permission


class User(DjangoObjectType):
    permissions = graphene.List(Permission)

    class Meta:
        model = get_user_model()
        filter_fields = ['email']
        interfaces = [graphene.relay.Node]

    def resolve_permissions(self, info):
        return None
