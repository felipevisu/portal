class DocumentFileStatus:
    WAITING = "waiting"
    APPROVED = "approved"
    REFUSED = "refused"

    CHOICES = [
        (WAITING, "Aguardando"),
        (APPROVED, "Aprovado"),
        (REFUSED, "Recusado"),
    ]


class DocumentLoadOptions:
    EMPTY = "empty"
    CNC = "consult_correctional_negative_certificate"

    CHOICES = [(EMPTY, "Nenhum"), (CNC, "Certidão Negativa Correcionalo")]
