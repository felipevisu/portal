import graphene

from ...event import models
from ..account.types import User
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType
from .enums import EventTypesEnum


class Event(ModelObjectType):
    id = graphene.GlobalID(required=True)
    type = graphene.String()
    user = graphene.Field(lambda: User)
    parameters = graphene.JSONString()
    date = graphene.Date()

    class Meta:
        model = models.Event
        interfaces = [graphene.relay.Node]


class EventCountableConnection(CountableConnection):
    class Meta:
        node = Event
