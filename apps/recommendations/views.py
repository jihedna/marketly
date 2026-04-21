"""Recommendations page with filters."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from .models import Recommendation


@method_decorator(login_required, name="dispatch")
class RecommendationsView(View):
    template_name = "recommendations/home.html"

    def get(self, request):
        qs = Recommendation.objects.filter(user=request.user)
        kind = request.GET.get("kind")
        if kind:
            qs = qs.filter(kind=kind)
        kinds = Recommendation._meta.get_field("kind").choices
        return render(
            request,
            self.template_name,
            {"recommendations": qs, "kinds": kinds, "selected_kind": kind},
        )
