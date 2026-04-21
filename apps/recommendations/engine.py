"""Rule-based recommendation engine."""
from __future__ import annotations

from typing import Any

INDUSTRY_CHANNELS = {
    "ecommerce": ["Meta Ads", "Google Shopping", "Lifecycle email", "TikTok"],
    "saas": ["Google Search", "LinkedIn Ads", "Webinars", "Content/SEO"],
    "retail": ["Meta Ads", "Google Local", "Influencers", "SMS"],
    "fintech": ["Google Search", "LinkedIn Ads", "PR", "Content/SEO"],
    "healthcare": ["Google Search", "Content/SEO", "Email", "Events"],
    "default": ["Meta Ads", "Google Search", "Lifecycle email", "Content/SEO"],
}

PLAN_FOR_BUDGET = {
    "lt5k": "Starter",
    "5_25k": "Pro",
    "25_100k": "Pro",
    "gt100k": "Enterprise",
}


def _industry_key(industry: str) -> str:
    i = (industry or "").lower()
    for k in INDUSTRY_CHANNELS:
        if k in i:
            return k
    return "default"


def generate_recommendations(
    *,
    user,
    company: dict[str, Any],
    campaign: dict[str, Any],
    solution: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    objective = campaign.get("objective", "awareness")
    industry_key = _industry_key(company.get("industry", ""))
    channels = INDUSTRY_CHANNELS[industry_key]
    plan = PLAN_FOR_BUDGET.get(campaign.get("budget", ""), "Starter")

    recs: list[dict[str, Any]] = [
        {
            "kind": "strategy",
            "title": f"Focus on {objective} with a full-funnel approach",
            "description": (
                "Prioritize a narrow objective and support it across creative, channels, "
                "and lifecycle to compound results."
            ),
            "payload": {"objective": objective},
        },
        {
            "kind": "channel",
            "title": f"Channel mix: {', '.join(channels[:3])}",
            "description": (
                f"For {industry_key if industry_key != 'default' else 'your industry'} companies, "
                f"these channels produce the best early traction."
            ),
            "payload": {"channels": channels},
        },
        {
            "kind": "budget",
            "title": "Suggested budget allocation",
            "description": (
                "45% paid acquisition, 20% creative, 15% content/SEO, 10% lifecycle email, "
                "10% analytics/experimentation."
            ),
            "payload": {"allocation": [45, 20, 15, 10, 10]},
        },
        {
            "kind": "service",
            "title": "Add creative testing to your workflow",
            "description": (
                "Teams that rotate 6-10 concepts per month sustainably reduce CAC by 15-30%."
            ),
            "payload": {},
        },
        {
            "kind": "plan",
            "title": f"{plan} plan matches your profile",
            "description": (
                "Recommended based on your budget and objective. You can upgrade at any time."
            ),
            "payload": {"plan": plan},
        },
    ]
    if solution:
        recs.insert(
            0,
            {
                "kind": "strategy",
                "title": f"Deep-dive on {solution.get('title')}",
                "description": str(solution.get("overview", "")),
                "payload": {"solution_slug": solution.get("slug")},
            },
        )
    return recs
