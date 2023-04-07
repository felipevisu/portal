import re
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
from django.core.exceptions import ValidationError
from django.core.files import File

from portal.document import DocumentFileStatus

from ...document.models import DocumentFile


def get_data(api, token, cnpj):
    parameters = "?token={}&timeout=600&cnpj={}".format(token, cnpj)
    url = api + parameters
    response = requests.get(url)

    parsed = response.json()
    if response.status_code in range(600, 799):
        raise ValidationError(parsed.get("code_message", ""))

    data = parsed.get("data", [])
    if len(data) == 0:
        raise ValidationError("Nenhum dado encontrado")

    return data[0]


def load_file(expiration_date, file_url, document):
    try:
        file_temp = NamedTemporaryFile(delete=True)
        file_temp.write(urlopen(file_url).read())
        file_temp.flush()
        file_name = file_url.split("/")[-1]
        document_file = DocumentFile.objects.create(
            document=document,
            status=DocumentFileStatus.APPROVED,
            expiration_date=expiration_date,
        )
        document_file.file.save(file_name, File(file_temp))
        document.default_file = document_file
        document.save()
        return document_file
    except:
        raise ValidationError("Erro ao processar o arquivo")


def correctional_negative_certificate(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/cgu/cnc-tipo1"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("data_validade", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)


def labor_debit_clearance_certifiacate(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/tst/cndt"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)
