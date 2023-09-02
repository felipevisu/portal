from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from portal.customer.models import Client
from portal.document.models import DocumentLoad


class Command(BaseCommand):
    help = "Delete old document loads"

    def handle(self, *args, **kwargs):
        clients = Client.objects.exclude(schema_name="public")
        for client in clients:
            with schema_context(client.schema_name):
                DocumentLoad.objects.all().delete()
