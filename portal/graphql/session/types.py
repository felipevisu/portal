import graphene

from ...session import models
from ..channel.dataloaders import ChannelByIdLoader
from ..channel.types import Channel
from ..core.connection import CountableConnection
from ..core.types import ModelObjectType


class Session(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    content = graphene.JSONString()
    is_published = graphene.Boolean()
    date = graphene.DateTime()
    channel = graphene.Field(Channel, required=False)

    class Meta:
        model = models.Session
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_channel(root, info):
        return ChannelByIdLoader(info.context).load(root.channel_id)


class SessionCountableConnection(CountableConnection):
    class Meta:
        node = Session
