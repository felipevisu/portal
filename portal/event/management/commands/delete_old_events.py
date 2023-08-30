from django.core.management.base import BaseCommand

from portal.document.models import Document


class Command(BaseCommand):
    help = "Delete old events"

    def handle(self, *args, **kwargs):
        documents = Document.objects.all()
        for document in documents:
            events = document.events.all()[5:]
            if len(events) > 0:
                for event in events:
                    event.delete()
