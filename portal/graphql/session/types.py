import graphene

from ...session import models
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType


class Session(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    content = graphene.JSONString()
    is_published = graphene.Boolean()
    date = graphene.DateTime()

    class Meta:
        model = models.Session
        interfaces = [graphene.relay.Node]


class SessionCountableConnection(CountableConnection):
    class Meta:
        node = Session
