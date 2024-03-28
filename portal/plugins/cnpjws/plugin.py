from django.template.loader import render_to_string

from ...document import DocumentFileStatus, DocumentLoadOptions
from ...document.models import Document, DocumentFile
from ..base_plugin import BasePlugin, ConfigurationTypeField
from .lib import fetch_document, save_file


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
        response, path = save_file(html, document)
        document_file = DocumentFile.objects.create(
            document=document, status=DocumentFileStatus.APPROVED
        )
        document_file.file.name = path
        document_file.save()
        document.default_file = document_file
        document.save()
        return document_file

    def consult_document(self, entry, previous_value):
        if not self.active:
            return previous_value

        document = fetch_document(entry.document_number)
        return document
