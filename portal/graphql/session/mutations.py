import graphene

from ...core.permissions import SessionPermissions
from ...session import models
from ..core.mutations import ModelDeleteMutation, ModelMutation
from .types import Session


class SessionInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    content = graphene.JSONString()
    date = graphene.Date(required=False)
    time = graphene.Time(required=False)


class SessionCreate(ModelMutation):
    vehicle = graphene.Field(Session)

    class Arguments:
        input = SessionInput(required=True)

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)


class SessionUpdate(ModelMutation):
    vehicle = graphene.Field(Session)

    class Arguments:
        id = graphene.ID()
        input = SessionInput(required=True)

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)


class SessionDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Session
        permissions = (SessionPermissions.MANAGE_SESSIONS,)
