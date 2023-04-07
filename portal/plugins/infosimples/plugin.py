from ..base_plugin import BasePlugin, ConfigurationTypeField
from .tasks import (
    correctional_negative_certificate,
    employer_regularity_fgts,
    labor_debit_clearance_certifiacate,
)


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

    def consult_correctional_negative_certificate(self, document, previous_value):
        if not self.active:
            return previous_value

        token = self.config.get("token")
        return correctional_negative_certificate(token, document)

    def consult_labor_debit_clearance_certifiacate(self, document, previous_value):
        if not self.active:
            return previous_value

        token = self.config.get("token")
        return labor_debit_clearance_certifiacate(token, document)

    def consult_employer_regularity_fgts(self, document, previous_value):
        if not self.active:
            return previous_value

        token = self.config.get("token")
        return employer_regularity_fgts(token, document)
