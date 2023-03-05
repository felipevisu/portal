import graphene

from ..core.types import NonNullList
from .mutations import (
    ChannelActivate,
    ChannelCreate,
    ChannelDeactivate,
    ChannelDelete,
    ChannelUpdate,
)
from .resolvers import resolve_channel, resolve_channels
from .types import Channel


class Query(graphene.ObjectType):
    channel = graphene.Field(
        Channel,
        id=graphene.Argument(
            graphene.ID, description="ID of the channel.", required=False
        ),
        slug=graphene.Argument(
            graphene.String,
            description="Slug of the channel.",
            required=False,
        ),
        description="Look up a channel by ID or slug.",
    )
    channels = NonNullList(Channel, description="List of all channels.")

    @staticmethod
    def resolve_channel(_root, info, *, id=None, slug=None, **kwargs):
        return resolve_channel(info, id, slug)

    @staticmethod
    def resolve_channels(_root, _info, **kwargs):
        return resolve_channels()


class Mutation(graphene.ObjectType):
    channel_create = ChannelCreate.Field()
    channel_update = ChannelUpdate.Field()
    channel_delete = ChannelDelete.Field()
    channel_activate = ChannelActivate.Field()
    channel_deactivate = ChannelDeactivate.Field()
