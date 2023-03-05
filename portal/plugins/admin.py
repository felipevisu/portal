from django.contrib import admin

from .models import PluginConfiguration


@admin.register(PluginConfiguration)
class PluginConfigurationAdmin(admin.ModelAdmin):
    pass
