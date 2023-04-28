import logging
import re
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
from django.core.exceptions import ValidationError
from django.core.files import File

from portal.document import DocumentFileStatus

from ...core.utils.htmlToPDF import htmlToPDF
from ...document.models import DocumentFile


def get_data(api, token, cnpj, extra_params=""):
    parameters = "?token={}&timeout=600&cnpj={}&{}".format(token, cnpj, extra_params)
    url = api + parameters
    print(url)
    response = requests.get(url)

    parsed = response.json()
    if parsed["code"] in range(600, 799):
        raise ValidationError(message=parsed["code_message"])

    return parsed["data"][0]


def load_file(file_url, document, data={}):
    try:
        file_temp = NamedTemporaryFile(delete=True)
        file_temp.write(urlopen(file_url).read())
        file_temp.flush()
        file_name = file_url.split("/")[-1]
        document_file = DocumentFile.objects.create(
            document=document, status=DocumentFileStatus.APPROVED, *data
        )
        document_file.file.save(file_name, File(file_temp))
        document.default_file = document_file
        document.save()
        return document_file
    except Exception as e:
        logging.warning(str(e))
        raise ValidationError("Erro ao processar o arquivo")


def load_file_and_convert(file_url, document, data={}):
    try:
        pdf = htmlToPDF(file_url)
        file_temp = NamedTemporaryFile(delete=True)
        file_temp.write(pdf)
        file_name = file_url.split("/")[-1]
        file_name = file_name.split(".")[0]
        document_file = DocumentFile.objects.create(
            document=document, status=DocumentFileStatus.APPROVED, **data
        )
        document_file.file.save(file_name + ".pdf", File(file_temp))
        document.default_file = document_file
        document.save()
        return document_file
    except Exception as e:
        logging.warning(str(e))
        raise ValidationError("Erro ao processar o arquivo")


def jucesp(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    login = config.get("jucesp_login")
    password = config.get("jucesp_password")
    extra_params = f"login_cpf={login}&login_senha={password}"
    api = "https://api.infosimples.com/api/v2/consultas/junta-comercial/sp/simplifica"
    data = get_data(api, token, cnpj, extra_params)

    file_url = data.get("site_receipt", None)
    return load_file(file_url, document)


def mei(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    login = config.get("gov_br_login")
    password = config.get("gov_br_password")
    extra_params = f"login_cpf={login}&login_senha={password}"
    api = "https://api.infosimples.com/api/v2/consultas/receita-federal/mei"
    data = get_data(api, token, cnpj, extra_params)

    file_url = data.get("site_receipt", None)
    return load_file(file_url, document)


def tcu(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/tcu/cnp"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("data_validade", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file_and_convert(
        file_url, document, {"expiration_date": expiration_date}
    )


def cnd(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/receita-federal/pgfn"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(file_url, document, {"expiration_date": expiration_date})


def sefaz_mg(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    api = "https://api.infosimples.com/api/v2/consultas/sefaz/mg/certidao-debitos"

    consult = document.entry.consult.first()
    if not consult:
        raise ValidationError(
            "Para solicitar este arquivo faça primeiro uma consulta do cartão CNPJ"
        )

    token = config.get("token")
    cep = consult.response["estabelecimento"]["cep"]
    data = get_data(api, token, cnpj, "cep={}".format(cep))

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file_and_convert(
        file_url, document, {"expiration_date": expiration_date}
    )


def sefaz_sp(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/sefaz/sp/certidao-debitos"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(file_url, document, {"expiration_date": expiration_date})


def cnep(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/cgu/cnc-tipo1"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("data_validade", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(file_url, document, {"expiration_date": expiration_date})


def cndt(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/tst/cndt"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file(file_url, document, {"expiration_date": expiration_date})


def fgts(config, document):
    cnpj = document.entry.document_number
    cnpj = re.sub("[^0-9]", "", cnpj)
    token = config.get("token")
    api = "https://api.infosimples.com/api/v2/consultas/caixa/regularidade"
    data = get_data(api, token, cnpj)

    expiration_date = data.get("validade_fim_data", None)
    expiration_date = expiration_date.split("/")[::-1]
    expiration_date = "-".join(expiration_date)
    file_url = data.get("site_receipt", None)
    return load_file_and_convert(
        file_url, document, {"expiration_date": expiration_date}
    )
