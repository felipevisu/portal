import graphene
from graphene_django.filter import DjangoFilterConnectionField

from .mutations import SessionCreate, SessionDelete, SessionUpdate
from .resolvers import resolve_session, resolve_sessions
from .types import Session


class Query(graphene.ObjectType):
    session = graphene.Field(
        Session,
        id=graphene.Argument(graphene.ID),
        slug=graphene.String(),
    )
    sessions = DjangoFilterConnectionField(Session)

    def resolve_sessions(self, info, *args, **kwargs):
        return resolve_sessions(info)

    def resolve_session(self, info, id=None):
        return resolve_session(info, id)


class Mutation(graphene.ObjectType):
    session_create = SessionCreate.Field()
    session_update = SessionUpdate.Field()
    session_delete = SessionDelete.Field()
