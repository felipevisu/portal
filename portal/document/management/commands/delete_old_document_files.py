from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from portal.customer.models import Client
from portal.document.models import Document


def delete_document_files():
    documents = Document.objects.all()
    for document in documents:
        files = document.files.exclude(id=document.default_file_id).all()[3:]
        for file in files:
            file.delete()


class Command(BaseCommand):
    help = "Delete old document files"

    def handle(self, *args, **kwargs):
        clients = Client.objects.exclude(schema_name="public")
        for client in clients:
            with schema_context(client.schema_name):
                delete_document_files()
