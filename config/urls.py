"""URL configuration for the Marketly project."""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = "apps.core.views.custom_404"

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    # allauth only handles social login flow for us
    path("accounts/social/", include("allauth.socialaccount.urls")),
    path("accounts/social/", include("allauth.socialaccount.providers.google.urls")),
    path("accounts/social/", include("allauth.socialaccount.providers.facebook.urls")),
    path("accounts/social/", include("allauth.socialaccount.providers.github.urls")),
    # Stripe webhook (outside i18n so Stripe can POST cleanly)
    path("billing/webhook/", include("apps.billing.webhook_urls")),
]

urlpatterns += i18n_patterns(
    path("", include(("apps.core.urls", "core"), namespace="core")),
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("services/", include(("apps.services.urls", "services"), namespace="services")),
    path("solutions/", include(("apps.solutions.urls", "solutions"), namespace="solutions")),
    path("chatbot/", include(("apps.chatbot.urls", "chatbot"), namespace="chatbot")),
    path(
        "recommendations/",
        include(("apps.recommendations.urls", "recommendations"), namespace="recommendations"),
    ),
    path("billing/", include(("apps.billing.urls", "billing"), namespace="billing")),
    path("dashboard/", include(("apps.accounts.dashboard_urls", "dashboard"), namespace="dashboard")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
