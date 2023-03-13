import graphene

from ...event import models
from ..account.types import User
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType
from ..document.dataloaders import DocumentByIdLoader
from .enums import EventTypesEnum


class Event(ModelObjectType):
    id = graphene.GlobalID(required=True)
    type = EventTypesEnum(description="Order event type.")
    document = graphene.Field("portal.graphql.document.types.Document")
    user = graphene.Field(lambda: User)
    parameters = graphene.JSONString()
    date = graphene.DateTime()

    class Meta:
        model = models.Event
        interfaces = [graphene.relay.Node]

    def resolve_type(self, info):
        print(self.get_type_display())
        return self.get_type_display()

    def resolve_document(self, info):
        if self.document_id:
            document_id = self.document_id
        else:
            return None
        return DocumentByIdLoader(info.context).load(document_id)


class EventCountableConnection(CountableConnection):
    class Meta:
        node = Event
