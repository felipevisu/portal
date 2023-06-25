import time

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
                document = Document.objects.create(
                    entry=entry,
                    expires=False,
                    name="CNPJ",
                    load_type=DocumentLoadOptions.CNPJ,
                )
            if document and not document.default_file:
                print(f"Updating document for entry: {entry.name}")
                load_new_document_from_api(
                    document_id=document.id, user_id=None, delay=False
                )
                document.refresh_from_db()
                document.is_published = True
                document.save()
                time.sleep(20)
