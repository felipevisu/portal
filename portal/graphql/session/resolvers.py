import graphene

from ...session import models


def resolve_session(_, global_session_id=None):
    _, session_pk = graphene.Node.from_global_id(global_session_id)
    session = models.Session.objects.filter(pk=session_pk).first()
    return session


def resolve_sessions(info):
    user = info.context.user
    return models.Session.objects.visible_to_user(user)
