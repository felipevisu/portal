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
    CNDT = "consult_labor_debit_clearance_certifiacate"
    FGTS = "consult_employer_regularity_fgts"

    CHOICES = [
        (EMPTY, "Nenhum"),
        (CNC, "Certidão Negativa Correcionalo"),
        (CNDT, "Certidão negativa de débitos trabalhistas"),
        (FGTS, "Regularidade do empregador (FGTS)"),
    ]


class DocumentLoadStatus:
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"

    CHOICES = [(PENDING, "Pendendte"), (SUCCESS, "Bem sucedido"), (ERROR, "Erro")]
