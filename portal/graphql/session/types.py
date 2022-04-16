import graphene
from graphene_django import DjangoObjectType

from ...session import models


class Session(DjangoObjectType):

    class Meta:
        model = models.Session
        filter_fields = ['is_published']
        interfaces = [graphene.relay.Node]
