from ..settings import *  # noqa

SECRET_KEY = "NOTREALLY"

ALLOWED_CLIENT_HOSTS = ["www.example.com"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

INSTALLED_APPS.append("portal.tests")  # noqa

AUTH_PASSWORD_VALIDATORS = []

DATABASE_CONNECTION_REPLICA_NAME = DATABASE_CONNECTION_DEFAULT_NAME  # noqa
