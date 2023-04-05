from ..base_plugin import BasePlugin, ConfigurationTypeField
from .tasks import correctional_negative_certificate


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
        # Convert to dict to easier take config elements
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = configuration

    def consult_correctional_negative_certificate(self, document, previous_value):
        if not self.active:
            return previous_value

        return correctional_negative_certificate(self.config.get("token"), document)
