import logging
import re
from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
from django.core.exceptions import ValidationError
from django.core.files import File

from portal.document import DocumentFileStatus, DocumentLoadOptions

from ...core.utils.htmlToPDF import htmlToPDF
from ...document.models import Document, DocumentFile


class LoadFileMixin:
    def load_file(self, file_url: str, data: dict = {}) -> DocumentFile:
        try:
            document = self.document
            file_temp = NamedTemporaryFile(delete=True)
            file_temp.write(urlopen(file_url).read())
            file_temp.flush()
            file_name = file_url.split("/")[-1]
            document_file = DocumentFile.objects.create(
                document=document, status=DocumentFileStatus.APPROVED, **data
            )
            document_file.file.save(file_name, File(file_temp))
            document.default_file = document_file
            document.save()
            return document_file
        except Exception as e:
            logging.warning(str(e))
            raise ValidationError("Erro ao processar o arquivo")


class LoadAndConvertFileMixin:
    def load_file(self, file_url: str, data: dict = {}) -> DocumentFile:
        try:
            document = self.document
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


class AbstractLoader(ABC):
    @abstractmethod
    def __init__(self, api: str, config: dict, document: Document):
        self.api = api
        self.config = config
        self.document = document

    def get_extra_params(self) -> str:
        return ""

    def get_expiration_date(self, data: dict):
        pass

    def get_data(self) -> dict or None:
        extra_params = self.get_extra_params()
        cnpj = re.sub("[^0-9]", "", self.document.entry.document_number)
        parameters = "?token={}&timeout=600&cnpj={}&{}".format(
            self.config.get("token"), cnpj, extra_params
        )
        url = self.api + parameters
        response = requests.get(url)

        parsed = response.json()
        if parsed["code"] in range(600, 799):
            raise ValidationError(message=parsed["code_message"])

        data = parsed["data"][0]
        return data

    def load_file(file_url: str, data: dict = {}) -> DocumentFile:
        pass

    def load(self):
        data = self.get_data()
        file_url = data.get("site_receipt", None)
        file = self.load_file(file_url=file_url, data=self.get_expiration_date(data))
        return file


class JUCESP(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/junta-comercial/sp/simplifica",
    ):
        super().__init__(api, config, document)

    def get_extra_params(self) -> str:
        login = self.config.get("jucesp_login")
        password = self.config.get("jucesp_password")
        extra_params = f"login_cpf={login}&login_senha={password}"
        return extra_params


class MEI(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/receita-federal/mei",
    ):
        super().__init__(api, config, document)

    def get_extra_params(self) -> str:
        login = self.config.get("gov_br_login")
        password = self.config.get("gov_br_password")
        extra_params = f"login_cpf={login}&login_senha={password}"
        return extra_params


class TCU(AbstractLoader, LoadAndConvertFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/tcu/cnp",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("data_validade", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class CND(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/receita-federal/pgfn",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class SEFAZMG(AbstractLoader, LoadAndConvertFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/sefaz/mg/certidao-debitos",
    ):
        super().__init__(api, config, document)

    def get_extra_params(self) -> str:
        consult = self.document.entry.consult.first()
        if not consult:
            raise ValidationError(
                "Para solicitar este arquivo faça primeiro uma consulta do cartão CNPJ"
            )
        cep = consult.response["estabelecimento"]["cep"]
        extra_params = "cep={}".format(cep)
        return extra_params

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class SEFAZSP(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/sefaz/sp/certidao-debitos",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class CNEP(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/cgu/cnc-tipo1",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class CNDT(AbstractLoader, LoadFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/tst/cndt",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


class FGTS(AbstractLoader, LoadAndConvertFileMixin):
    def __init__(
        self,
        document: Document,
        config: dict,
        api: str = "https://api.infosimples.com/api/v2/consultas/caixa/regularidade",
    ):
        super().__init__(api, config, document)

    def get_expiration_date(self, data: dict):
        expiration_date = data.get("validade_fim_data", None)
        expiration_date = expiration_date.split("/")[::-1]
        expiration_date = "-".join(expiration_date)
        return {"expiration_date": expiration_date}


def loader_factory(type: str) -> AbstractLoader:
    LOAD_MAP = {
        DocumentLoadOptions.CNEP: CNEP,
        DocumentLoadOptions.CNDT: CNDT,
        DocumentLoadOptions.CND: CND,
        DocumentLoadOptions.FGTS: FGTS,
        DocumentLoadOptions.SEFAZ_MG: SEFAZMG,
        DocumentLoadOptions.SEFAZ_SP: SEFAZSP,
        DocumentLoadOptions.TCU: TCU,
        DocumentLoadOptions.MEI: MEI,
        DocumentLoadOptions.JUCESP: JUCESP,
    }

    if type not in LOAD_MAP:
        return None

    return LOAD_MAP[type]
