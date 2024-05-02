import os

from django.conf import settings

DEFAULT_EMAIL_TEMPLATES_PATH = os.path.join(
    settings.BASE_DIR, "portal/plugins/admin_email/default_email_templates"
)

SET_STAFF_PASSWORD_TEMPLATE_FIELD = "set_staff_password_template"
STAFF_PASSWORD_RESET_TEMPLATE_FIELD = "staff_password_reset_template"


TEMPLATE_FIELDS = [
    SET_STAFF_PASSWORD_TEMPLATE_FIELD,
    STAFF_PASSWORD_RESET_TEMPLATE_FIELD,
]

SET_STAFF_PASSWORD_DEFAULT_TEMPLATE = "set_password.html"
STAFF_PASSWORD_RESET_DEFAULT_TEMPLATE = "password_reset.html"

SET_STAFF_PASSWORD_SUBJECT_FIELD = "set_staff_password_subject"
STAFF_PASSWORD_RESET_SUBJECT_FIELD = "staff_password_reset_subject"


SET_STAFF_PASSWORD_DEFAULT_SUBJECT = "Set Your Dashboard Password"
STAFF_PASSWORD_RESET_DEFAULT_SUBJECT = "Reset Your Dashboard Password"


PLUGIN_ID = "portal.notifications.admin_email"
