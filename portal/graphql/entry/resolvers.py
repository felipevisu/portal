from django.db.models import Exists, OuterRef

from ...channel.models import Channel
from ...core.db.utils import get_database_connection_name
from ...entry import models
from ..channel import ChannelQsContext
from ..core.utils import from_global_id_or_error


def resolve_entry_type(_, global_entry_type_id=None, slug=None):
    if global_entry_type_id:
        _, entry_type_pk = from_global_id_or_error(global_entry_type_id)
        entry_type = models.EntryType.objects.filter(pk=entry_type_pk).first()
    else:
        entry_type = models.EntryType.objects.filter(slug=slug).first()
    return entry_type


def resolve_entry_types():
    return models.EntryType.objects.all()


def resolve_category(_, global_category_id=None, slug=None):
    if global_category_id:
        _, category_pk = from_global_id_or_error(global_category_id)
        category = models.Category.objects.filter(pk=category_pk).first()
    else:
        category = models.Category.objects.filter(slug=slug).first()
    return category


def resolve_categories():
    return models.Category.objects.all()


def resolve_entry(info, global_entry_id=None, slug=None, channel_slug=None):
    database_connection_name = get_database_connection_name(info.context)
    user = info.context.user
    qs = models.Entry.objects.using(database_connection_name).visible_to_user(
        user, channel_slug=channel_slug
    )
    print(user)
    if global_entry_id:
        _, entry_pk = from_global_id_or_error(global_entry_id)
        return qs.filter(id=entry_pk).first()
    else:
        return qs.filter(slug=slug).first()


def resolve_entries(info, channel_slug=None):
    database_connection_name = get_database_connection_name(info.context)
    user = info.context.user
    qs = (
        models.Entry.objects.all()
        .using(database_connection_name)
        .visible_to_user(user, channel_slug)
    )
    if channel_slug:
        channels = Channel.objects.filter(slug=str(channel_slug))
        entry_channel_listings = models.EntryChannelListing.objects.filter(
            Exists(channels.filter(pk=OuterRef("channel_id")))
        )
        qs = qs.filter(Exists(entry_channel_listings.filter(entry_id=OuterRef("pk"))))
    return ChannelQsContext(qs=qs, channel_slug=channel_slug)
