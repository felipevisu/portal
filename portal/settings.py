import ast
import os.path
import re
from datetime import timedelta
from typing import List

import dj_database_url
import dj_email_url
import pkg_resources
import sentry_sdk
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv()


def get_list(text):
    return [item.strip() for item in text.split(",")]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = get_bool_from_env("DEBUG", True)

if not SECRET_KEY and DEBUG:
    SECRET_KEY = get_random_secret_key()

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

SITE_ID = 1

ALLOWED_HOSTS = get_list(os.environ.get("ALLOWED_HOSTS", "*"))

CSRF_TRUSTED_ORIGINS = get_list(
    os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "http://*.localhost:5173, http://localhost:8000"
    )
)

CORS_ALLOWED_ORIGIN_REGEXES_LIST = get_list(
    os.environ.get(
        "CORS_ALLOWED_ORIGIN_REGEXES", "^http://\w+\.{localhost|127.0.0.1}\:\d{4}$"
    )
)

CORS_ALLOWED_ORIGIN_REGEXES = [
    re.compile(regex_pattern) for regex_pattern in CORS_ALLOWED_ORIGIN_REGEXES_LIST
]

CORS_ALLOW_ALL_ORIGINS = DEBUG

SHARED_APPS = [
    "storages",
    "corsheaders",
    "django_filters",
    "django_tenants",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.auth",
    "django.contrib.admin",
    "django_celery_beat",
    "django_celery_results",
    "portal.account",
    "portal.customer",
    "portal.plugins",
]

TENANT_APPS = [
    "portal.attribute",
    "portal.channel",
    "portal.core",
    "portal.document",
    "portal.entry",
    "portal.event",
    "portal.investment",
    "portal.session",
]

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

TENANT_MODEL = "customer.Client"

TENANT_DOMAIN_MODEL = "customer.Domain"

AUTH_USER_MODEL = "account.User"

TENANT_SUBFOLDER_PREFIX = "clientes"

MIDDLEWARE = [
    "django_tenants.middleware.TenantSubfolderMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "portal.core.middleware.jwt_refresh_token_middleware",
]

ROOT_URLCONF = "portal.urls"

ROOT_URLCONF = "portal.urls_tenants"
PUBLIC_SCHEMA_URLCONF = "portal.urls_public"

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.site.context_processors.site",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]


WSGI_APPLICATION = "portal.wsgi.application"

DATABASE_CONNECTION_DEFAULT_NAME = "default"

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://portal:portal@db:5432/portal")

DATABASES = {
    DATABASE_CONNECTION_DEFAULT_NAME: dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        engine="django_tenants.postgresql_backend",
    ),
}

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    }
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

BUILTIN_PLUGINS = [
    "portal.plugins.admin_email.plugin.AdminEmailPlugin",
    "portal.plugins.sendgrid.plugin.SendgridEmailPlugin",
    "portal.plugins.cnpjws.plugin.CNPJWSPlugin",
    "portal.plugins.infosimples.plugin.InfoSimplesPlugin",
]

EXTERNAL_PLUGINS = []
installed_plugins = pkg_resources.iter_entry_points("portal.plugins")
for entry_point in installed_plugins:
    plugin_path = "{}.{}".format(entry_point.module_name, entry_point.attrs[0])
    if plugin_path not in BUILTIN_PLUGINS and plugin_path not in EXTERNAL_PLUGINS:
        if entry_point.name not in INSTALLED_APPS:
            INSTALLED_APPS.append(entry_point.name)
        EXTERNAL_PLUGINS.append(plugin_path)

PLUGINS = BUILTIN_PLUGINS + EXTERNAL_PLUGINS

GRAPHQL_MIDDLEWARE: List[str] = []
GRAPHQL_PAGINATION_LIMIT = 100
PLAYGROUND_ENABLED = DEBUG

SENTRY_DNS = os.environ.get("SENTRY_DNS", None)
if SENTRY_DNS and not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_DNS,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

AUTHENTICATION_BACKENDS = [
    "portal.core.auth_backend.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_HEADERS = {"Access-Control-Allow-Origin": "*"}
AWS_DEFAULT_ACL = "public-read"
AWS_LOCATION = "static"

DEFAULT_FILE_STORAGE = "portal.core.storages.S3MediaStorage"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


STATIC_ROOT: str = os.path.join(PROJECT_ROOT, "static")
STATIC_URL: str = os.environ.get("STATIC_URL", "/static/")
STATICFILES_DIRS = [
    ("images", os.path.join(PROJECT_ROOT, "portal", "static", "images"))
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
if not DEBUG:
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_CONNECTION_DEFAULT_NAME = "default"
DATABASE_CONNECTION_REPLICA_NAME = "default"

JWT_EXPIRE = False
JWT_TTL_ACCESS = timedelta(seconds=10)
JWT_TTL_APP_ACCESS = timedelta(seconds=10)
JWT_TTL_REFRESH = timedelta(days=30)
JWT_TTL_REQUEST_EMAIL_CHANGE = timedelta(seconds=3600)
JWT_MANAGER_PATH = "portal.core.jwt_manager.JWTManager"

EMAIL_URL = os.environ.get("EMAIL_URL", None)
SENDGRID_USERNAME = os.environ.get("SENDGRID_USERNAME")
SENDGRID_PASSWORD = os.environ.get("SENDGRID_PASSWORD")
if not EMAIL_URL and SENDGRID_USERNAME and SENDGRID_PASSWORD:
    EMAIL_URL = (
        f"smtp://{SENDGRID_USERNAME}"
        f":{SENDGRID_PASSWORD}@smtp.sendgrid.net:587/?tls=True"
    )

email_config = dj_email_url.parse(
    EMAIL_URL or "console://demo@example.com:console@example/"
)

EMAIL_FILE_PATH = email_config["EMAIL_FILE_PATH"]
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
EMAIL_USE_SSL = email_config["EMAIL_USE_SSL"]

# CELERY SETTINGS
USE_AWS_SQS = get_bool_from_env("USE_AWS_SQS", True)
if USE_AWS_SQS:
    CELERY_BROKER_URL = f"sqs://{AWS_ACCESS_KEY_ID}:{AWS_SECRET_ACCESS_KEY}@"
    AWS_SQS_URL = os.environ.get("AWS_SQS_URL")
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "region": "us-east-1",  # your AWS SQS region
        "predefined_queues": {
            "celery": {  ## the name of the SQS queue
                "url": AWS_SQS_URL,
                "access_key_id": AWS_ACCESS_KEY_ID,
                "secret_access_key": AWS_SECRET_ACCESS_KEY,
            }
        },
    }
else:
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis:127.0.0.1:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "django-db")


ENABLE_DEBUG_TOOLBAR = DEBUG
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ["debug_toolbar", "graphiql_debug_toolbar"]
    MIDDLEWARE.append("portal.graphql.middleware.DebugToolbarMiddleware")
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
