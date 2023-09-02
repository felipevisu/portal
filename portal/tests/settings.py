from ..settings import *

SECRET_KEY = "NOTREALLY"

ALLOWED_CLIENT_HOSTS = ["www.example.com"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

INSTALLED_APPS.append("portal.tests")
INSTALLED_APPS.remove("django_tenants")

MIDDLEWARE.remove("django_tenants.middleware.TenantSubfolderMiddleware"),

DATABASE_ROUTERS = []

AUTH_PASSWORD_VALIDATORS = []

DATABASE_CONNECTION_REPLICA_NAME = DATABASE_CONNECTION_DEFAULT_NAME

JWT_EXPIRE = True
