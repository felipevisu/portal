import graphene

from portal.graphql.channel.dataloaders import ChannelByIdLoader

from ....entry import models
from ...channel.types import Channel
from ...core.types.model import ModelObjectType


class EntryChannelListing(ModelObjectType):
    id = graphene.GlobalID(required=True)
    is_published = graphene.Boolean(required=True)
    is_active = graphene.Boolean(required=True)
    channel = graphene.Field(Channel, required=True)

    class Meta:
        model = models.EntryChannelListing
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_channel(root, info, **kwargs):
        return ChannelByIdLoader(info.context).load(root.channel_id)
