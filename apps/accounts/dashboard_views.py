"""Authenticated dashboard."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator(login_required, name="dispatch")
class DashboardHomeView(TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["projects"] = user.campaign_projects.select_related("solution").all()[:6]
        ctx["strategies"] = user.strategy_plans.all()[:6]
        ctx["conversations"] = user.chat_conversations.all()[:5]
        ctx["recommendations"] = user.recommendations.order_by("-created_at")[:5]
        ctx["subscription"] = user.subscriptions.order_by("-created_at").first()
        ctx["transactions"] = user.payment_transactions.order_by("-created_at")[:5]
        return ctx
