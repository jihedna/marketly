"""Pricing plans, subscriptions and payment transactions."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PricingPlan(models.Model):
    INTERVAL_CHOICES = [("month", _("Monthly")), ("year", _("Yearly")), ("once", _("One-time"))]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    tagline = models.CharField(max_length=160, blank=True, default="")
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="USD")
    interval = models.CharField(max_length=16, choices=INTERVAL_CHOICES, default="month")
    features = models.JSONField(default=list, blank=True)
    is_recommended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=120, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "price_cents"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    @property
    def price_display(self) -> str:
        if self.price_cents == 0:
            return "Free"
        return f"${self.price_cents / 100:.0f}"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("inactive", _("Inactive")),
        ("trialing", _("Trialing")),
        ("active", _("Active")),
        ("past_due", _("Past due")),
        ("canceled", _("Canceled")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="inactive")
    stripe_subscription_id = models.CharField(max_length=120, blank=True, default="")
    stripe_customer_id = models.CharField(max_length=120, blank=True, default="")
    current_period_end = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("succeeded", _("Succeeded")),
        ("failed", _("Failed")),
        ("refunded", _("Refunded")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_transactions"
    )
    plan = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, blank=True, null=True)
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    stripe_session_id = models.CharField(max_length=200, blank=True, default="", db_index=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, default="")
    receipt_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def amount_display(self) -> str:
        return f"${self.amount_cents/100:.2f}"
