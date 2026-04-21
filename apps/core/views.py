"""Core views: home, contact, helpers."""
from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import activate, gettext as _
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.solutions.catalog import MARKETING_SOLUTIONS


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["solutions_preview"] = MARKETING_SOLUTIONS[:6]
        ctx["stats"] = [
            {"value": "320%", "label": _("Average ROAS uplift")},
            {"value": "1.8M+", "label": _("Leads generated")},
            {"value": "96%", "label": _("Client retention")},
            {"value": "45", "label": _("Countries served")},
        ]
        ctx["testimonials"] = [
            {
                "quote": _(
                    "Marketly transformed how we approach campaign planning. "
                    "We shipped our strongest quarter ever."
                ),
                "author": "Amira Ben Saïd",
                "role": _("Head of Growth, Nova Retail"),
            },
            {
                "quote": _(
                    "The AI recommendations saved us weeks of research and "
                    "helped us reallocate our ad spend with confidence."
                ),
                "author": "David Laurent",
                "role": _("CMO, Helix Analytics"),
            },
            {
                "quote": _(
                    "From branding to paid ads, it's a single place where our "
                    "team plans, executes, and reports."
                ),
                "author": "Yousra El Amrani",
                "role": _("Founder, Atlas Studio"),
            },
        ]
        return ctx


class ContactView(View):
    template_name = "core/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if not (name and email and message):
            messages.error(request, _("Please fill in all required fields."))
            return render(request, self.template_name, {"name": name, "email": email, "message": message})
        send_mail(
            subject=_("New contact message from %(name)s") % {"name": name},
            message=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
        messages.success(request, _("Thanks! We'll get back to you shortly."))
        return HttpResponseRedirect(reverse_lazy("core:contact"))


def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


@require_POST
def set_theme(request):
    theme = request.POST.get("theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"
    response = JsonResponse({"ok": True, "theme": theme})
    response.set_cookie("preferred_theme", theme, max_age=60 * 60 * 24 * 365, samesite="Lax")
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        if profile is not None:
            profile.preferred_theme = theme
            profile.save(update_fields=["preferred_theme"])
    return response


@require_POST
def set_language_pref(request):
    lang = request.POST.get("language", "en")
    if not any(lang == code for code, _label in settings.LANGUAGES):
        lang = "en"
    activate(lang)
    request.session["preferred_language"] = lang
    response = JsonResponse({"ok": True, "language": lang})
    response.set_cookie("preferred_language", lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        if profile is not None:
            profile.preferred_language = lang
            profile.save(update_fields=["preferred_language"])
    return response
