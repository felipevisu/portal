from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import JSONField

from ..core.permissions import PluginsPermissions


class PluginConfiguration(models.Model):
    identifier = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    configuration = JSONField(
        blank=True, null=True, default=dict, encoder=DjangoJSONEncoder
    )

    class Meta:
        permissions = ((PluginsPermissions.MANAGE_PLUGINS.codename, "Manage plugins."),)

    def __str__(self):
        return f"{self.identifier}, active: {self.active}"


class EmailTemplate(models.Model):
    plugin_configuration = models.ForeignKey(
        PluginConfiguration, related_name="email_templates", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    value = models.TextField()

    def __str__(self):
        return self.name
