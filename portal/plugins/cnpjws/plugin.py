from tempfile import NamedTemporaryFile

import weasyprint
from django.core.files import File
from django.template.loader import render_to_string

from ...document import DocumentFileStatus, DocumentLoadOptions
from ...document.models import Document, DocumentFile
from ..base_plugin import BasePlugin, ConfigurationTypeField
from .lib import fetch_document


class CNPJWSPlugin(BasePlugin):
    PLUGIN_ID = "portal.consult.cnpj_ws"
    PLUGIN_NAME = "CNPJWS"
    DEFAULT_ACTIVE = True

    DEFAULT_CONFIGURATION = [
        {"name": "public_api", "value": True},
        {"name": "token", "value": ""},
    ]

    CONFIG_STRUCTURE = {
        "public_api": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Permite três consultas por minuto",
            "label": "Utilizar API pública",
        },
        "token": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Necessário em caso de uso comercial",
            "label": "Token",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert to dict to easier take config elements
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = configuration

    def consult(self, document: Document, previous_value):
        if not self.active:
            return previous_value

        if not document.load_type == DocumentLoadOptions.CNPJ:
            return previous_value

        response = fetch_document(document.entry.document_number)
        html = render_to_string("documents/cnpj.html", response)
        pdf = weasyprint.HTML(string=html).write_pdf()
        file_temp = NamedTemporaryFile(delete=True)
        file_temp.write(pdf)
        file_name = "cnpj.pdf"
        document_file = DocumentFile.objects.create(
            document=document, status=DocumentFileStatus.APPROVED
        )
        document_file.file.save(file_name, File(file_temp))
        document.default_file = document_file
        document.save()
        return document_file

    def consult_document(self, entry, previous_value):
        if not self.active:
            return previous_value

        document = fetch_document(entry.document_number)
        return document
