from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("name",)}),
        (_("Informações de contato"), {"fields": ("email", "phone", "address")}),
        (_("Gerenciamento"), {"fields": ("active", "created_at", "updated_at")})
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name", "email", "phone", "active")
    search_fields = ("name", "email", "phone")
    ordering = ("name",)