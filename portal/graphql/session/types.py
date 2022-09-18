import graphene
from graphene_django import DjangoObjectType

from ...session import models
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType


class Session(ModelObjectType):

    class Meta:
        model = models.Session
        interfaces = [graphene.relay.Node]


class SessionCountableConnection(CountableConnection):
    class Meta:
        node = Session
