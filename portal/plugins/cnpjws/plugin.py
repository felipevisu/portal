import re

import requests
from django.core.exceptions import ValidationError

from ..base_plugin import BasePlugin, ConfigurationTypeField


class CNPJWSPlugin(BasePlugin):
    PLUGIN_ID = "portal.consult.cnpj_ws"
    PLUGIN_NAME = "CNPJWS"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False

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

    def consult_document(self, entry, previous_value):
        if not self.active:
            return previous_value

        cnpj = entry.document_number
        cnpj = re.sub("[^0-9]", "", cnpj)
        url = "https://publica.cnpj.ws/cnpj/{}".format(cnpj)
        response = requests.get(url)

        if response.status_code == 200:
            return response.json(), self.PLUGIN_NAME

        if response.status_code == 429:
            raise ValidationError("Límite de três consultas por minuto")

        if response.status_code == 400:
            parsed = response.json()
            message = parsed.get("detalhes", None)
            raise ValidationError(message)

        raise ValidationError("Erro na requisição")
