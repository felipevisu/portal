from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from portal.document import DocumentLoadOptions
from portal.document.models import Document
from portal.document.tasks import load_new_document_from_api


class Command(BaseCommand):
    help = "Displays current time"

    def handle(self, *args, **kwargs):
        expiration = datetime.today() + timedelta(days=2)
        documents = (
            Document.objects.select_related("entry")
            .prefetch_related("entry__channel_listings")
            .filter(
                is_published=True,
                entry__channel_listings__is_published=True,
                entry__channel_listings__is_active=True,
                expires=True,
                default_file__expiration_date__lte=expiration,
            )
            .exclude(load_type=DocumentLoadOptions.EMPTY)
            .distinct()
        )

        for document in documents:
            print(
                f"Updating document: {document.name} with the API {document.load_type}."
            )
            load = load_new_document_from_api(
                document_id=document.id, user_id=None, delay=False
            )
            print(f"Result: {load.status}")
