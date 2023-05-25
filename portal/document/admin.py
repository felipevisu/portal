from django.contrib import admin

from .models import DocumentLoad


@admin.register(DocumentLoad)
class DocumentLoad(admin.ModelAdmin):
    list_display = ["document", "status", "created"]
