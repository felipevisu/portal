class EventTypes:
    DOCUMENT_UPDATED_BY_PROVIDER = "document_updated_by_provider"
    DOCUMENT_UPDATED_BY_STAFF = "document_updated_by_staff"
    PROVIDER_NOTIFIED_ABOUT_EXPIRED_DOCUMENT = (
        "provider_notified_about_expired_document"
    )
    NEW_DOCUMENT_REQUESTED_BY_STAFF = "new_document_requested_by_staff"

    CHOICES = [
        (DOCUMENT_UPDATED_BY_PROVIDER, "Documento atualizado pelo fornecedor"),
        (DOCUMENT_UPDATED_BY_STAFF, "Documento atualizado pelo administrador"),
        (
            PROVIDER_NOTIFIED_ABOUT_EXPIRED_DOCUMENT,
            "Fornecedor foi notificado sobre documento expirado",
        ),
        (
            NEW_DOCUMENT_REQUESTED_BY_STAFF,
            "Novo documento foi requisitado pelo administrador",
        ),
    ]
