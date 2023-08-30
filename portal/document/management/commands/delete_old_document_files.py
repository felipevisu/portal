from django.core.management.base import BaseCommand

from portal.document.models import Document, DocumentFile


class Command(BaseCommand):
    help = "Delete old document files"

    def handle(self, *args, **kwargs):
        not_delete = Document.objects.filter(default_file_id__isnull=False).values_list(
            "default_file_id", flat=True
        )
        DocumentFile.objects.exclude(id__in=not_delete).delete()
