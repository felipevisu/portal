from .models import Consult


def delete_old_consults(entry):
    total = Consult.objects.filter(entry=entry).count()
    if total > 5:
        items = Consult.objects.filter(entry=entry)[5:]
        for item in items:
            item.delete()