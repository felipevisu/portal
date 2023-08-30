from django.core.management.base import BaseCommand

from portal.document.models import DocumentLoad


class Command(BaseCommand):
    help = "Delete old document loads"

    def handle(self, *args, **kwargs):
        DocumentLoad.objects.all().delete()
