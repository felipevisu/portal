class AdminNotifyEvent:
    ACCOUNT_SET_STAFF_PASSWORD = "account_set_staff_password"
    ACCOUNT_STAFF_RESET_PASSWORD = "account_staff_reset_password"
    DOCUMENT_RECEIVED = "document_received"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_DECLINED = "document_declined"
    REQUEST_NEW_DOCUMENT = "request_new_document"

    CHOICES = [
        ACCOUNT_SET_STAFF_PASSWORD,
        ACCOUNT_STAFF_RESET_PASSWORD,
        DOCUMENT_RECEIVED,
        DOCUMENT_APPROVED,
        DOCUMENT_DECLINED,
        REQUEST_NEW_DOCUMENT,
    ]


class NotifyEventType(AdminNotifyEvent):
    CHOICES = AdminNotifyEvent.CHOICES
