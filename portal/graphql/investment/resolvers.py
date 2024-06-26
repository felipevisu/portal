from ...channel.models import Channel
from ...investment import models
from ..core.utils import from_global_id_or_error


def resolve_investment(info, global_investment_id, month, year):
    user = info.context.user
    if global_investment_id:
        _, investment_pk = from_global_id_or_error(global_investment_id, "Investment")
        investment = (
            models.Investment.objects.visible_to_user(user)
            .filter(pk=investment_pk)
            .first()
        )
    else:
        investment = (
            models.Investment.objects.visible_to_user(user)
            .filter(month=month, year=year)
            .first()
        )
    return investment


def resolve_investments(info, channel_slug):
    user = info.context.user
    qs = models.Investment.objects.visible_to_user(user)
    if channel_slug:
        channel = Channel.objects.filter(slug=str(channel_slug)).first()
        qs = qs.filter(channel=channel)
    return qs
