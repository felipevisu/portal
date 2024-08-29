from django.contrib import admin

from .models import DocumentFile, DocumentLoad


@admin.register(DocumentLoad)
class DocumentLoad(admin.ModelAdmin):
    list_display = ["document", "status", "created"]


@admin.register(DocumentFile)
class DocumentFile(admin.ModelAdmin):
    list_display = ["id", "file", "document", "status"]
