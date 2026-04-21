"""Solutions: listing, detail, configuration wizard, plan detail."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View

from apps.recommendations.engine import generate_recommendations
from apps.recommendations.models import Recommendation

from .catalog import MARKETING_SOLUTIONS, SOLUTION_BY_SLUG
from .forms import CampaignStepForm, CompanyStepForm
from .models import CampaignProject, MarketingSolution, StrategyPlan
from .planner import generate_plan


class SolutionsListView(View):
    template_name = "solutions/list.html"

    def get(self, request):
        # Use DB objects if seeded, otherwise fall back to static catalog.
        solutions = list(MarketingSolution.objects.filter(is_active=True))
        if not solutions:
            solutions = MARKETING_SOLUTIONS
        return render(request, self.template_name, {"solutions": solutions})


class SolutionDetailView(View):
    template_name = "solutions/detail.html"

    def get(self, request, slug: str):
        solution = SOLUTION_BY_SLUG.get(slug)
        db_obj = MarketingSolution.objects.filter(slug=slug).first()
        if not solution and not db_obj:
            raise Http404
        ctx = {
            "solution": db_obj or solution,
            "start_url": reverse("solutions:start", args=[slug]),
        }
        return render(request, self.template_name, ctx)


@method_decorator(login_required, name="dispatch")
class StartSolutionView(View):
    """Three-step wizard kicked off from a solution card."""

    template_name = "solutions/wizard.html"

    def _state_key(self, slug: str) -> str:
        return f"solution_wizard::{slug}"

    def _get_solution(self, slug: str) -> dict:
        return SOLUTION_BY_SLUG.get(slug) or {
            "slug": slug,
            "title": slug.replace("-", " ").title(),
        }

    def get(self, request, slug: str):
        state = request.session.get(self._state_key(slug), {})
        step = int(request.GET.get("step", state.get("step", 1)) or 1)
        company_form = CompanyStepForm(instance=request.user.company)
        campaign_form = CampaignStepForm(initial=state.get("campaign", {}))
        generated_plan = state.get("plan")
        return render(
            request,
            self.template_name,
            {
                "solution": self._get_solution(slug),
                "slug": slug,
                "step": step,
                "company_form": company_form,
                "campaign_form": campaign_form,
                "plan": generated_plan,
            },
        )

    def post(self, request, slug: str):
        state_key = self._state_key(slug)
        state = request.session.get(state_key, {})
        step = int(request.POST.get("step", 1))
        solution = self._get_solution(slug)

        if step == 1:
            form = CompanyStepForm(request.POST, instance=request.user.company)
            if not form.is_valid():
                return render(
                    request,
                    self.template_name,
                    {
                        "solution": solution,
                        "slug": slug,
                        "step": 1,
                        "company_form": form,
                        "campaign_form": CampaignStepForm(initial=state.get("campaign", {})),
                    },
                )
            form.save()
            state["company"] = {
                "name": request.user.company.name,
                "industry": request.user.company.industry,
                "size": request.user.company.size,
                "website": request.user.company.website,
            }
            state["step"] = 2
            request.session[state_key] = state
            return redirect(f"{reverse('solutions:start', args=[slug])}?step=2")

        if step == 2:
            form = CampaignStepForm(request.POST)
            if not form.is_valid():
                return render(
                    request,
                    self.template_name,
                    {
                        "solution": solution,
                        "slug": slug,
                        "step": 2,
                        "company_form": CompanyStepForm(instance=request.user.company),
                        "campaign_form": form,
                    },
                )
            state["campaign"] = form.cleaned_data
            state["step"] = 3
            plan_data = generate_plan(
                solution=solution,
                company=state.get("company", {}),
                campaign=state["campaign"],
            )
            state["plan"] = plan_data
            request.session[state_key] = state
            return redirect(f"{reverse('solutions:start', args=[slug])}?step=3")

        if step == 3 and "save" in request.POST:
            plan_data = state.get("plan")
            if not plan_data:
                messages.error(request, _("Please complete the previous steps first."))
                return redirect(f"{reverse('solutions:start', args=[slug])}?step=1")
            db_solution = MarketingSolution.objects.filter(slug=slug).first()
            project = CampaignProject.objects.create(
                user=request.user,
                solution=db_solution,
                name=f"{solution.get('title', slug.title())} — {state.get('campaign', {}).get('objective', 'plan')}",
                status="planning",
                company_snapshot=state.get("company", {}),
                campaign_details=state.get("campaign", {}),
            )
            plan = StrategyPlan.objects.create(
                user=request.user,
                project=project,
                solution=db_solution,
                title=project.name,
                summary=plan_data["executive_summary"],
                plan_data=plan_data,
            )
            recs = generate_recommendations(
                user=request.user,
                company=state.get("company", {}),
                campaign=state.get("campaign", {}),
                solution=solution,
            )
            for item in recs:
                Recommendation.objects.create(
                    user=request.user,
                    project=project,
                    kind=item["kind"],
                    title=item["title"],
                    description=item["description"],
                    payload=item.get("payload", {}),
                )
            request.session.pop(state_key, None)
            messages.success(request, _("Your strategy plan has been saved."))
            return redirect(plan.get_absolute_url())

        return redirect(reverse("solutions:start", args=[slug]))


@method_decorator(login_required, name="dispatch")
class StrategyPlanDetailView(View):
    template_name = "solutions/plan_detail.html"

    def get(self, request, pk: int):
        plan = get_object_or_404(StrategyPlan, pk=pk, user=request.user)
        return render(request, self.template_name, {"plan": plan, "data": plan.plan_data})
