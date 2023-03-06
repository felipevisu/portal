class AdminNotifyEvent:
    ACCOUNT_SET_STAFF_PASSWORD = "account_set_staff_password"
    ACCOUNT_STAFF_RESET_PASSWORD = "account_staff_reset_password"
    DOCUMENT_UPDATED_BY_PROVIDER = "document_updated_by_provider"
    REQUEST_NEW_DOCUMENT_FROM_PROVIDER = "request_new_document_from_provider"

    CHOICES = [
        ACCOUNT_SET_STAFF_PASSWORD,
        ACCOUNT_STAFF_RESET_PASSWORD,
        DOCUMENT_UPDATED_BY_PROVIDER,
        REQUEST_NEW_DOCUMENT_FROM_PROVIDER,
    ]


class NotifyEventType(AdminNotifyEvent):
    CHOICES = AdminNotifyEvent.CHOICES
