from django.core.management.base import BaseCommand

from portal.document.models import Document, DocumentFile


class Command(BaseCommand):
    help = "Delete old files"

    def handle(self, *args, **kwargs):
        not_delete = Document.objects.all().values_list("default_file_id", flat=True)
        files = DocumentFile.objects.all()
        for file in files:
            if file.id not in not_delete:
                file.delete()
