import re

import requests
from django.core.exceptions import ValidationError


def fetch_document(cnpj: str):
    cnpj = re.sub("[^0-9]", "", cnpj)
    url = "https://publica.cnpj.ws/cnpj/{}".format(cnpj)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    if response.status_code == 429:
        raise ValidationError("Límite de três consultas por minuto")

    if response.status_code == 400:
        parsed = response.json()
        message = parsed.get("detalhes", None)
        raise ValidationError(message)
