"""Template context processors for Marketly."""
from __future__ import annotations

from django.conf import settings


def site_context(request):
    theme = request.COOKIES.get("preferred_theme", "light")
    return {
        "BRAND_NAME": "Marketly",
        "BRAND_TAGLINE": "Marketing strategies that grow brands.",
        "SITE_URL": settings.SITE_URL,
        "PREFERRED_THEME": theme,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
    }
