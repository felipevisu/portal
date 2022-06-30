import graphene
from graphene_django import DjangoObjectType

from ...session import models
from ..core.connection import ContableConnection
from .filters import SessionFilter


class Session(DjangoObjectType):

    class Meta:
        model = models.Session
        filterset_class = SessionFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection
