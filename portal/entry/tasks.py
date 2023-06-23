from django.core.exceptions import ValidationError

from .models import Consult
from .utils import delete_old_consults


def consult_document(entry, manager, user):
    manager.consult_document
    response = manager.consult_document(entry)

    if not response:
        raise ValidationError("Nenhuma API conseguiu retornar esta consulta")

    Consult.objects.create(entry=entry, plugin="", response=response)
    delete_old_consults(entry)
