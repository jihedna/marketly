"""Service catalog: high-level product capabilities presented on /services/.

Services are managed dynamically from the Django admin and seeded with
`python manage.py seed_demo`.
"""
from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """A service offered by Marketly — e.g. data analysis, AI chatbot, etc."""

    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(_("title"), max_length=140)
    tagline = models.CharField(_("short description"), max_length=240)
    description = models.TextField(_("description"), blank=True, default="")
    icon = models.CharField(
        _("icon"),
        max_length=8,
        default="✨",
        help_text=_("Emoji or short glyph used as the card illustration."),
    )
    accent_color = models.CharField(
        _("accent color"),
        max_length=32,
        default="violet",
        help_text=_(
            "Tailwind-style hue used for the card accent: orange, pink, "
            "violet, teal, green."
        ),
    )
    cta_label = models.CharField(_("CTA label"), max_length=60, blank=True, default="")
    cta_url = models.CharField(
        _("CTA url"),
        max_length=200,
        blank=True,
        default="",
        help_text=_(
            "Absolute path or named-route target. Leave empty to default to "
            "the pricing page."
        ),
    )
    related_plan = models.ForeignKey(
        "billing.PricingPlan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="services",
        verbose_name=_("related plan"),
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.title
