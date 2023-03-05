import ast
import os.path
from datetime import timedelta
from pathlib import Path

import dj_database_url
import django_on_heroku
import pkg_resources
from dotenv import load_dotenv

load_dotenv()


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = get_bool_from_env("DEBUG", True)

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

SITE_ID = 1

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "storages",
    # django modules
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # apps
    "portal.account",
    "portal.channel",
    "portal.core",
    "portal.document",
    "portal.entry",
    "portal.investment",
    "portal.plugins",
    "portal.session",
    # libs
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "django_filters",
    "debug_toolbar",
    "graphene_django",
    "graphiql_debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "graphiql_debug_toolbar.middleware.DebugToolbarMiddleware",
    "portal.core.middleware.jwt_refresh_token_middleware",
]

ROOT_URLCONF = "portal.urls"

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "portal.wsgi.application"

DATABASE_CONNECTION_DEFAULT_NAME = "default"

DB_USER = os.environ.get("DB_USER", "")

DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

DB_NAME = os.environ.get("DB_NAME", "")

DATABASES = {
    DATABASE_CONNECTION_DEFAULT_NAME: dj_database_url.config(
        default=f"postgres://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}",
        conn_max_age=600,
    ),
}

AUTH_USER_MODEL = "account.User"

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

BUILTIN_PLUGINS = ["portal.plugins.admin_email.plugin.AdminEmailPlugin"]

EXTERNAL_PLUGINS = []
installed_plugins = pkg_resources.iter_entry_points("saleor.plugins")
for entry_point in installed_plugins:
    plugin_path = "{}.{}".format(entry_point.module_name, entry_point.attrs[0])
    if plugin_path not in BUILTIN_PLUGINS and plugin_path not in EXTERNAL_PLUGINS:
        if entry_point.name not in INSTALLED_APPS:
            INSTALLED_APPS.append(entry_point.name)
        EXTERNAL_PLUGINS.append(plugin_path)

PLUGINS = BUILTIN_PLUGINS + EXTERNAL_PLUGINS

GRAPHENE = {
    "SCHEMA": "portal.graphql.schema.schema",
    "SCHEMA_OUTPUT": "schema.graphql",
    "SCHEMA_INDENT": 2,
    "MIDDLEWARE": [
        "portal.graphql.middleware.JWTMiddleware",
    ],
}

AUTHENTICATION_BACKENDS = [
    "portal.core.auth_backend.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_LOCATION = "static"
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_HEADERS = {"Access-Control-Allow-Origin": "*"}
AWS_DEFAULT_ACL = "public-read"

DEFAULT_FILE_STORAGE = "portal.core.storages.S3MediaStorage"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATICFILES_DIRS = [
    ("images", os.path.join(PROJECT_ROOT, "portal", "static", "images"))
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASE_CONNECTION_DEFAULT_NAME = "default"
DATABASE_CONNECTION_REPLICA_NAME = "default"

JWT_EXPIRE = False
JWT_TTL_ACCESS = timedelta(seconds=10)
JWT_TTL_APP_ACCESS = timedelta(seconds=10)
JWT_TTL_REFRESH = timedelta(days=30)
JWT_TTL_REQUEST_EMAIL_CHANGE = timedelta(seconds=3600)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = os.environ.get("EMAIL_POST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")
EMAIL_USE_SSL = get_bool_from_env("EMAIL_USE_SSL", False)
EMAIL_USE_TLS = get_bool_from_env("EMAIL_USE_TLS", True)

# CELERY SETTINGS
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "")
CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", None)

django_on_heroku.settings(locals())
