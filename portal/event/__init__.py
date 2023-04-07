class EventTypes:
    DOCUMENT_CREATED = "document_create"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"

    DOCUMENT_RECEIVED = "document_received"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_DECLINED = "document_declined"
    DOCUMENT_REQUESTED = "document_requested"
    DOCUMENT_LOADED_FROM_API = "document_loaded_from_api"

    ENTRY_CREATED = "entry_created"
    ENTRY_UPDATED = "entry_updated"
    ENTRY_DELETED = "entry_deleted"

    CHOICES = [
        (DOCUMENT_CREATED, "Documento adicionado"),
        (DOCUMENT_UPDATED, "Documento atualizado"),
        (DOCUMENT_DELETED, "Documento excluído"),
        (DOCUMENT_RECEIVED, "Documento recebido"),
        (DOCUMENT_APPROVED, "Documento aprovado"),
        (DOCUMENT_DECLINED, "Documento recusado"),
        (DOCUMENT_REQUESTED, "Documento solicitado pela plataforma"),
        (DOCUMENT_LOADED_FROM_API, "Documento atualizado por API"),
        (ENTRY_CREATED, "Cadastro adicionado"),
        (ENTRY_UPDATED, "Cadastro atualizado"),
        (ENTRY_DELETED, "Cadastro excluído"),
    ]
