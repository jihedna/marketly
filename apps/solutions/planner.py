"""Generate a personalized marketing plan based on user inputs.

This is a deterministic rule-based generator that returns a structured plan.
It's intentionally standalone so a real AI provider can be plugged in later.
"""
from __future__ import annotations

from typing import Any

BUDGET_RANGES = {
    "lt5k": (2_000, 5_000),
    "5_25k": (5_000, 25_000),
    "25_100k": (25_000, 100_000),
    "gt100k": (100_000, 250_000),
}

DURATION_WEEKS = {"4w": 4, "3m": 13, "6m": 26, "12m": 52}


CHANNELS_BY_OBJECTIVE = {
    "awareness": ["Meta Ads", "TikTok", "YouTube", "PR & influencers"],
    "leads": ["Google Search", "LinkedIn Ads", "Webinars", "Email"],
    "conversion": ["Google Shopping", "Meta Retargeting", "Lifecycle email", "Affiliates"],
    "retention": ["Lifecycle email", "SMS", "Loyalty program", "Community"],
    "launch": ["PR", "Influencers", "Meta Ads", "Waitlist email"],
}


def _format_currency(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.1f}k"
    return f"${amount:.0f}"


def generate_plan(
    *, solution: dict[str, Any], company: dict[str, Any], campaign: dict[str, Any]
) -> dict[str, Any]:
    """Return a dict representing the full marketing plan."""
    objective = campaign.get("objective", "awareness")
    budget_range = BUDGET_RANGES.get(campaign.get("budget"), (2_000, 5_000))
    duration_weeks = DURATION_WEEKS.get(campaign.get("duration"), 13)
    industry = company.get("industry") or "your industry"
    company_name = company.get("name") or "Your company"
    channels = CHANNELS_BY_OBJECTIVE.get(objective, ["Meta Ads", "Google Search", "Lifecycle email"])

    monthly_low, monthly_high = budget_range
    months = max(1, round(duration_weeks / 4.33))
    total_low = monthly_low * months
    total_high = monthly_high * months

    allocation = [
        {"channel": channels[0], "share": 40},
        {"channel": channels[1] if len(channels) > 1 else "Creative production", "share": 25},
        {"channel": channels[2] if len(channels) > 2 else "Lifecycle email", "share": 20},
        {"channel": channels[3] if len(channels) > 3 else "Analytics & optimization", "share": 15},
    ]

    timeline = []
    milestones = [
        ("Week 1-2", "Research & setup", "Audit, competitor analysis, measurement plan"),
        ("Week 3-4", "Creative & build", "Creative production, campaign builds, tracking"),
        ("Week 5-8", "Launch & test", "Launch with A/B tests on creative and audiences"),
        ("Month 3+", "Scale & optimize", "Double down on winners, refresh creative"),
    ]
    for label, title, detail in milestones:
        timeline.append({"label": label, "title": title, "detail": detail})

    kpis = [
        {"name": "Impressions", "target": f"{int(max(50_000, monthly_low*25)):,}/month"},
        {"name": "CTR", "target": "1.8%+"},
        {"name": "CAC", "target": "Down 15% quarter-over-quarter"},
        {"name": "ROAS", "target": "3.5×+ on paid media"},
        {"name": "Lead volume", "target": f"{max(100, int(monthly_low/50)):,}/month"},
    ]

    return {
        "executive_summary": (
            f"A {months}-month plan to help {company_name} in {industry} achieve "
            f"'{objective}' via a focused mix of {', '.join(channels[:3])}."
        ),
        "business_analysis": {
            "strengths": [
                f"Clear focus on {objective} outcomes",
                f"Industry expertise in {industry}",
            ],
            "opportunities": [
                "Scaled creative testing",
                "Full-funnel measurement",
                "Retention via lifecycle email",
            ],
            "risks": ["Creative fatigue", "Platform bid inflation", "Attribution gaps"],
        },
        "marketing_objectives": [
            f"Grow {objective} KPIs by 30-50% in {months} months",
            "Ship 12-20 experiments per quarter",
            "Reduce CAC by 15% quarter-over-quarter",
        ],
        "target_audience": campaign.get("audience", ""),
        "value_proposition": (
            f"{company_name} delivers measurable outcomes to {campaign.get('audience', 'your audience')}, "
            "grounded in data and premium creative."
        ),
        "recommended_channels": channels,
        "campaign_timeline": timeline,
        "budget_estimate": {
            "monthly_low": monthly_low,
            "monthly_high": monthly_high,
            "total_low": total_low,
            "total_high": total_high,
            "monthly_display": f"{_format_currency(monthly_low)} – {_format_currency(monthly_high)}/month",
            "total_display": f"{_format_currency(total_low)} – {_format_currency(total_high)} over {months} months",
            "allocation": allocation,
        },
        "kpis": kpis,
        "optimization_recommendations": [
            "Rotate creatives every 10-14 days to fight fatigue",
            "Run incrementality tests on top spending channels",
            "Adopt MMM-lite quarterly to validate channel mix",
            "Build a UGC pipeline to sustain volume",
        ],
        "next_steps": [
            "Approve the strategy brief",
            "Kick-off workshop (90 min)",
            "Week 1 audit + measurement setup",
            "Week 3 creative launch",
        ],
        "meta": {
            "solution_slug": solution.get("slug"),
            "solution_title": str(solution.get("title", "")),
            "objective": objective,
            "budget_bucket": campaign.get("budget"),
            "duration_bucket": campaign.get("duration"),
            "months": months,
        },
    }
