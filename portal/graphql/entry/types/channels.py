import graphene

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
