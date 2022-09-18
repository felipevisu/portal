import graphene

from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField
from .filters import SessionFilterInput
from .mutations import SessionBulkDelete, SessionCreate, SessionDelete, SessionUpdate
from .resolvers import resolve_session, resolve_sessions
from .sorters import SessionSortingInput
from .types import Session, SessionCountableConnection


class Query(graphene.ObjectType):
    session = graphene.Field(
        Session,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    sessions = FilterConnectionField(
        SessionCountableConnection,
        sort_by=SessionSortingInput(),
        filter=SessionFilterInput()
    )

    def resolve_session(self, info, id=None):
        return resolve_session(info, id)

    def resolve_sessions(self, info, **kwargs):
        qs = resolve_sessions(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, SessionCountableConnection)


class Mutation(graphene.ObjectType):
    session_create = SessionCreate.Field()
    session_update = SessionUpdate.Field()
    session_delete = SessionDelete.Field()
    session_bulk_delete = SessionBulkDelete.Field()
