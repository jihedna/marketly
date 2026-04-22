"""Services views."""
from __future__ import annotations

from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Service


class ServicesListView(TemplateView):
    template_name = "services/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = Service.objects.filter(is_active=True)
        return ctx
