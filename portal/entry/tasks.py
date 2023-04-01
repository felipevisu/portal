from .models import Consult
from .utils import delete_old_consults


def consult_document(entry, manager, user):
    manager.consult_document
    response, plugin = manager.consult_document(entry)
    Consult.objects.create(entry=entry, plugin=plugin, response=response)
    delete_old_consults(entry)
