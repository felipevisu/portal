import graphene

from ...channel.models import Channel
from ...session import models


def resolve_session(_, global_session_id=None):
    _, session_pk = graphene.Node.from_global_id(global_session_id)
    session = models.Session.objects.filter(pk=session_pk).first()
    return session


def resolve_sessions(info, channel_slug):
    user = info.context.user
    qs = models.Session.objects.visible_to_user(user)
    if channel_slug:
        channel = Channel.objects.filter(slug=str(channel_slug)).first()
        qs = qs.filter(channel=channel)
    return qs
