from django.contrib import admin

from .models import User


@admin.register(User)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["email", "is_superuser", "is_staff"]
