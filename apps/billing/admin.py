from django.contrib import admin

from .models import PaymentTransaction, PricingPlan, Subscription


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price_cents", "currency", "interval", "is_active", "is_recommended")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("is_active", "is_recommended", "interval")
    search_fields = ("name", "slug")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email",)


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount_cents", "currency", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "stripe_session_id")
