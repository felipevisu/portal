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
    CNEP = "cnep"
    CND = "cnd"
    CNDT = "cndt"
    FGTS = "fgts"
    SEFAZ_MG = "sefaz_mg"
    SEFAZ_SP = "sefaz_sp"

    CHOICES = [
        (EMPTY, "empty"),
        (CNEP, "cnep"),
        (CND, "cnd"),
        (CNDT, "cndt"),
        (FGTS, "fgts"),
        (SEFAZ_MG, "sefaz_mg"),
        (SEFAZ_SP, "sefaz_sp"),
    ]


class DocumentLoadStatus:
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"

    CHOICES = [(PENDING, "Pendendte"), (SUCCESS, "Bem sucedido"), (ERROR, "Erro")]
