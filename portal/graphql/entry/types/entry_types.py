import graphene

from ....entry import models
from ...core.connection import CountableConnection
from ...core.types import ModelObjectType


class EntryType(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()

    class Meta:
        model = models.EntryType
        interfaces = [graphene.relay.Node]


class EntryTypeCountableConnection(CountableConnection):
    class Meta:
        node = EntryType
