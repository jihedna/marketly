from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "accent_color", "order", "is_active", "related_plan")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "accent_color")
    search_fields = ("title", "slug", "tagline", "description")
    prepopulated_fields = {"slug": ("title",)}
