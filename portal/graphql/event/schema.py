import graphene

from ...core.permissions import EventPermissions
from ..core.connection import create_connection_slice
from ..core.fields import ConnectionField
from .resolvers import resolve_events
from .types import Event, EventCountableConnection


class Query(graphene.ObjectType):
    events = ConnectionField(
        EventCountableConnection,
        permissions=[
            EventPermissions.MANAGE_EVENTS,
        ],
    )

    def resolve_events(self, info, *args, **kwargs):
        qs = resolve_events()
        return create_connection_slice(qs, info, kwargs, EventCountableConnection)
