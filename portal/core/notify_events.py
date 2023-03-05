class AdminNotifyEvent:
    ACCOUNT_SET_STAFF_PASSWORD = "account_set_staff_password"
    ACCOUNT_STAFF_RESET_PASSWORD = "account_staff_reset_password"

    CHOICES = [ACCOUNT_SET_STAFF_PASSWORD, ACCOUNT_STAFF_RESET_PASSWORD]


class NotifyEventType(AdminNotifyEvent):
    CHOICES = AdminNotifyEvent.CHOICES
