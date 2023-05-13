import graphene

from ...event import models
from ..account.dataloaders import UserByIdLoader
from ..account.types import User
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType
from ..document.dataloaders import DocumentByIdLoader
from .enums import EventTypesEnum


class Event(ModelObjectType):
    id = graphene.GlobalID(required=True)
    type = EventTypesEnum(description="Order event type.")
    document = graphene.Field("portal.graphql.document.types.Document")
    document_name = graphene.String()
    user = graphene.Field(lambda: User)
    user_email = graphene.String()
    parameters = graphene.JSONString()
    message = graphene.String()
    date = graphene.DateTime()

    class Meta:
        model = models.Event
        interfaces = [graphene.relay.Node]

    def resolve_type(self, info):
        return self.type

    def resolve_document(self, info):
        if self.document_id:
            document_id = self.document_id
        else:
            return None
        return DocumentByIdLoader(info.context).load(document_id)

    def resolver_user(self, info):
        if self.user_id:
            user_id = self.user_id
        else:
            return None
        return UserByIdLoader(info.context).load(user_id)


class EventCountableConnection(CountableConnection):
    class Meta:
        node = Event
