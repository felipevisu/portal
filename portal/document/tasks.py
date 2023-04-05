from django.core.exceptions import ValidationError


def load_new_document_from_api(document, manager):
    consult_func = getattr(manager, document.load_type)
    document = consult_func(document)

    if not document:
        raise ValidationError("Nenhuma API conseguiu retornar esta consulta")
