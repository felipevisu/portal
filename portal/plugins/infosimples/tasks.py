import logging
import re
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
import weasyprint
from django.core.exceptions import ValidationError
from django.core.files import File

from portal.document import DocumentFileStatus

from ...document.models import DocumentFile


def get_data(api, token, cnpj, extra_params=""):
    parameters = "?token={}&timeout=600&cnpj={}&{}".format(token, cnpj, extra_params)
    url = api + parameters
    response = requests.get(url)

    parsed = response.json()
    if parsed["code"] in range(600, 799):
        raise ValidationError(message=parsed["code_message"])

    return parsed["data"][0]


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
    except Exception as e:
        logging.warning(str(e))
        raise ValidationError("Erro ao processar o arquivo")


def load_file_and_convert(expiration_date, file_url, document):
    try:
        html = weasyprint.HTML(file_url)
        content_print_layout = "@page {size: A4 portrait; margin: 0;}"
        main_doc = html.render(
            stylesheets=[weasyprint.CSS(string=content_print_layout)]
        )
        pdf = main_doc.write_pdf()
        file_temp = NamedTemporaryFile(delete=True)
        file_temp.write(pdf)
        file_name = file_url.split("/")[-1]
        file_name = file_name.split(".")[0]
        document_file = DocumentFile.objects.create(
            document=document,
            status=DocumentFileStatus.APPROVED,
            expiration_date=expiration_date,
        )
        document_file.file.save(file_name + ".pdf", File(file_temp))
        document.default_file = document_file
        document.save()
        return document_file
    except Exception as e:
        logging.warning(str(e))
        raise ValidationError("Erro ao processar o arquivo")


def cnd(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/receita-federal/pgfn"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)


def sefaz_mg(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    api = "https://api.infosimples.com/api/v2/consultas/sefaz/mg/certidao-debitos"

    consult = document.entry.consult.first()
    if not consult:
        raise ValidationError(
            "Para solicitar este arquivo faça primeiro uma consulta do cartão CNPJ"
        )

    cep = consult.response["estabelecimento"]["cep"]
    data = get_data(api, token, cnpj, "cep={}".format(cep))

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file_and_convert(expiration_date, file_url, document)


def sefaz_sp(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/sefaz/sp/certidao-debitos"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)


def cnep(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/cgu/cnc-tipo1"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("data_validade", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)


def cndt(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/tst/cndt"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(expiration_date, file_url, document)


def fgts(token, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)

    api = "https://api.infosimples.com/api/v2/consultas/caixa/regularidade"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_fim_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file_and_convert(expiration_date, file_url, document)
