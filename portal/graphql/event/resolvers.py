from ...event.models import Event


def resolve_events():
    return Event.objects.all()
