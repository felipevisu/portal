from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from portal.customer.models import Client
from portal.document.models import Document


def delete_old_events():
    documents = Document.objects.all()
    for document in documents:
        events = document.events.all()[5:]
        if len(events) > 0:
            for event in events:
                event.delete()


class Command(BaseCommand):
    help = "Delete old events"

    def handle(self, *args, **kwargs):
        clients = Client.objects.exclude(schema_name="public")
        for client in clients:
            with schema_context(client.schema_name):
                delete_old_events()
