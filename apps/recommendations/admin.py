from django.contrib import admin

from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "kind", "created_at")
    list_filter = ("kind",)
    search_fields = ("title", "user__email")
