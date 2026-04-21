from django.contrib import admin

from .models import CampaignProject, MarketingSolution, StrategyPlan


@admin.register(MarketingSolution)
class MarketingSolutionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "order")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    list_filter = ("is_active",)


@admin.register(CampaignProject)
class CampaignProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "solution", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("name", "user__email")


@admin.register(StrategyPlan)
class StrategyPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "solution", "is_premium_unlocked", "created_at")
    search_fields = ("title", "user__email")
    list_filter = ("is_premium_unlocked",)
