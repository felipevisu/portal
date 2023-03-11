class EventTypes:
    DOCUMENT_RECEIVED = "document_received"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_DECLINED = "document_declined"
    DOCUMENT_REQUESTED = "document_requested"

    CHOICES = [
        (DOCUMENT_RECEIVED, "Documento recebido"),
        (DOCUMENT_APPROVED, "Documento aprovado"),
        (DOCUMENT_DECLINED, "Document recusado"),
        (DOCUMENT_REQUESTED, "Documento solicitado pela plataforma"),
    ]
