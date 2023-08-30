from django.core.management.base import BaseCommand

from portal.document.models import Document, DocumentFile


class Command(BaseCommand):
    help = "Delete old document files"

    def handle(self, *args, **kwargs):
        documents = Document.objects.all()
        for document in documents:
            files = document.files.exclude(id=document.default_file_id).all()[3:]
            for file in files:
                file.delete()
