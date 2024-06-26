from typing import Optional

from ...channel import models
from ..core.utils import from_global_id_or_error
from ..core.validators import validate_one_of_args_is_in_query
from .types import Channel


def resolve_channel(info, id: Optional[str], slug: Optional[str]):
    validate_one_of_args_is_in_query("id", id, "slug", slug)
    if id:
        _, db_id = from_global_id_or_error(id, Channel)
        channel = models.Channel.objects.filter(id=db_id).first()
    else:
        channel = models.Channel.objects.filter(slug=slug).first()

    if channel and channel.is_active:
        return channel
    if info.context.user:
        return channel

    return None


def resolve_channels(info):
    if info.context.user:
        return models.Channel.objects.all()
    return models.Channel.objects.filter(is_active=True)
