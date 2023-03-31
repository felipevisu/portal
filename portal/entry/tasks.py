from .models import Consult


def consult_document(entry, manager, user):
    manager.consult_document
    response, plugin = manager.consult_document(entry)
    Consult.objects.create(entry=entry, plugin=plugin, response=response)

    total = Consult.objects.filter(entry=entry).count()
    if total > 5:
        items = Consult.objects.filter(entry=entry)[5:]
        for item in items:
            item.delete()
