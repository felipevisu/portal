import os.path
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool)

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

SITE_ID = 1

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = ["http://localhost:3000", ]

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps
    'portal.account',
    'portal.core',
    'portal.investment',
    'portal.provider',
    'portal.session',
    'portal.vehicle',
    # libs
    'corsheaders',
    'django_filters',
    'debug_toolbar',
    'graphene_django',
    'graphiql_debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'graphiql_debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'

DATABASE_CONNECTION_DEFAULT_NAME = "default"

DB_USER = config("DB_USER")

DB_PASSWORD = config("DB_PASSWORD")

DB_NAME = config("DB_NAME")

DATABASES = {
    DATABASE_CONNECTION_DEFAULT_NAME: dj_database_url.config(
        default=f'postgres://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}',
        conn_max_age=600
    ),
}

AUTH_USER_MODEL = "account.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    }
]


LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

GRAPHENE = {
    "SCHEMA": "portal.graphql.schema.schema",
    'SCHEMA_OUTPUT': 'schema.graphql',
    'SCHEMA_INDENT': 2,
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware"
    ],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

STATIC_ROOT = 'staticfiles/'

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
