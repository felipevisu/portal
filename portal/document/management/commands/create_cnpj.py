from django.core.management.base import BaseCommand

from portal.document import DocumentLoadOptions
from portal.document.models import Document
from portal.document.tasks import load_new_document_from_api
from portal.entry.models import Entry


class Command(BaseCommand):
    help = "Displays current time"

    def handle(self, *args, **kwargs):
        entries = Entry.objects.all()

        for entry in entries:
            document = entry.documents.filter(
                load_type=DocumentLoadOptions.CNPJ
            ).first()
            if not document:
                print(f"Creating document for entry: {entry.name}")
                document = Document.objects.create(
                    entry=entry,
                    expires=False,
                    name="CNPJ",
                    load_type=DocumentLoadOptions.CNPJ,
                )
                load_new_document_from_api(document_id=document.id)
