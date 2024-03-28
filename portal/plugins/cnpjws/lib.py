import os
import re

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django_tenants.utils import parse_tenant_config_path

from portal.core.utils.shortUUID import generate_short_uuid


def fetch_document(cnpj: str):
    cnpj = re.sub("[^0-9]", "", cnpj)
    url = "https://publica.cnpj.ws/cnpj/{}".format(cnpj)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    if response.status_code == 429:
        raise ValidationError("Límite de três consultas por minuto")

    if response.status_code == 400:
        parsed = response.json()
        message = parsed.get("detalhes", None)
        raise ValidationError(message)


def get_upload_path(document):
    return os.path.join(
        "entry_%d" % document.entry.id,
        "document_%d" % document.id,
        "cnpj-{}.pdf".format(generate_short_uuid()),
    )


def save_file(html: str, document):
    url = "https://documents.publicidadedacidade.com.br/convert/"
    path = get_upload_path(document)
    prefix = parse_tenant_config_path("media") + "/"
    data = {
        "content": html,
        "contentType": "html",
        "bucketName": settings.AWS_STORAGE_BUCKET_NAME,
        "key": os.path.join(prefix, path),
    }
    response = requests.post(url=url, json=data)
    return response, path
