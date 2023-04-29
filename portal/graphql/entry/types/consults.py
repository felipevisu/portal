import graphene

from ....entry import models
from ...core.connection import CountableConnection
from ...core.types import ModelObjectType
from .entries import Entry


class Consult(ModelObjectType):
    id = graphene.GlobalID(required=True)
    entry = graphene.Field(lambda: Entry)
    response = graphene.JSONString()
    plugin = graphene.String()
    created = graphene.DateTime()

    class Meta:
        model = models.Consult
        interfaces = [graphene.relay.Node]


class ConsultCountableConnection(CountableConnection):
    class Meta:
        node = Consult
