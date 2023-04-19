from ...document import DocumentLoadOptions
from ...document.models import Document
from ..base_plugin import BasePlugin, ConfigurationTypeField
from .tasks import cnd, cndt, cnep, fgts, sefaz_mg, sefaz_sp

LOAD_MAP = {
    DocumentLoadOptions.CNEP: cnep,
    DocumentLoadOptions.CNDT: cndt,
    DocumentLoadOptions.CND: cnd,
    DocumentLoadOptions.FGTS: fgts,
    DocumentLoadOptions.SEFAZ_MG: sefaz_mg,
    DocumentLoadOptions.SEFAZ_SP: sefaz_sp,
}


class InfoSimplesPlugin(BasePlugin):
    PLUGIN_ID = "portal.consult.infosimples"
    PLUGIN_NAME = "InfoSimples"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False

    DEFAULT_CONFIGURATION = [
        {"name": "token", "value": ""},
    ]

    CONFIG_STRUCTURE = {
        "token": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Necessário em caso de uso comercial",
            "label": "Token",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = configuration

    def consult(self, document: Document, previous_value):
        if not self.active:
            return previous_value

        type = document.load_type

        type_in_load_options = (type, type) in DocumentLoadOptions.CHOICES
        if not type_in_load_options:
            return previous_value

        if type not in LOAD_MAP:
            return previous_value

        token = self.config.get("token")
        load_task = LOAD_MAP[type]
        return load_task(token, document)
