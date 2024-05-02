import os

from django.conf import settings
from tenant_schemas_celery.app import CeleryApp as TenantAwareCeleryApp

from .plugins import discover_plugins_modules

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portal.settings")

app = TenantAwareCeleryApp("portal")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: discover_plugins_modules(settings.PLUGINS))
