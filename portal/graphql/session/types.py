import graphene
from graphene_django import DjangoObjectType

from ...session import models
from .filters import SessionFilter


class Session(DjangoObjectType):

    class Meta:
        model = models.Session
        filterset_class = SessionFilter
        interfaces = [graphene.relay.Node]
