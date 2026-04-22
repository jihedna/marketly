"""Seed marketing solutions and pricing plans into the database."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.billing.models import PricingPlan
from apps.services.models import Service
from apps.solutions.catalog import MARKETING_SOLUTIONS
from apps.solutions.models import MarketingSolution

SERVICES = [
    {
        "slug": "data-analysis",
        "title": "Data analysis",
        "tagline": "Turn raw marketing data into clear, actionable insights.",
        "description": (
            "Aggregate analytics from every channel into a single story — spot "
            "trends, segments, and growth levers at a glance."
        ),
        "icon": "📊",
        "accent_color": "violet",
        "cta_label": "Start analyzing",
        "order": 1,
    },
    {
        "slug": "target-strategy",
        "title": "Target strategy planning",
        "tagline": "Pinpoint the audiences and channels that move your numbers.",
        "description": (
            "Persona mapping, JTBD research, and channel-fit scoring so your "
            "team focuses on the opportunities with the highest upside."
        ),
        "icon": "🎯",
        "accent_color": "pink",
        "cta_label": "Plan a strategy",
        "order": 2,
    },
    {
        "slug": "ai-chatbot",
        "title": "AI marketing assistant",
        "tagline": "Plan campaigns with an always-on AI strategist.",
        "description": (
            "Brainstorm ideas, draft briefs, and stress-test campaigns with "
            "Assistant Marketing IA — trained on marketing best practices."
        ),
        "icon": "🤖",
        "accent_color": "orange",
        "cta_label": "Open the assistant",
        "cta_url": "",
        "order": 3,
    },
    {
        "slug": "recommendations",
        "title": "Recommendation engine",
        "tagline": "Personalised playbooks for your audience and budget.",
        "description": (
            "Get channel, content, and budget suggestions tailored to your "
            "business context in seconds, saved to your dashboard."
        ),
        "icon": "💡",
        "accent_color": "teal",
        "cta_label": "Get recommendations",
        "order": 4,
    },
    {
        "slug": "campaign-optimization",
        "title": "Campaign optimization",
        "tagline": "Squeeze more ROAS from every euro spent.",
        "description": (
            "Automated budget reallocation, creative testing frameworks, and "
            "pacing monitors so your live campaigns always perform."
        ),
        "icon": "⚡",
        "accent_color": "green",
        "cta_label": "Optimize a campaign",
        "order": 5,
    },
    {
        "slug": "reporting-assistance",
        "title": "Reporting assistance",
        "tagline": "Executive-ready reports in one click.",
        "description": (
            "Auto-generated weekly and monthly reports with KPIs, commentary, "
            "and next-step recommendations for stakeholders."
        ),
        "icon": "📈",
        "accent_color": "violet",
        "cta_label": "Generate a report",
        "order": 6,
    },
]

PRICING_PLANS = [
    {
        "slug": "free",
        "name": "Free",
        "tagline": "Start planning your next marketing move.",
        "price_cents": 0,
        "interval": "month",
        "features": [
            "1 saved strategy",
            "Basic recommendations",
            "Community support",
        ],
        "is_recommended": False,
        "order": 1,
    },
    {
        "slug": "starter",
        "name": "Starter",
        "tagline": "For founders launching their first campaign.",
        "price_cents": 1900,
        "interval": "month",
        "features": [
            "5 saved strategies",
            "AI chatbot (200 messages/mo)",
            "Email support",
            "Downloadable PDF plans",
        ],
        "is_recommended": False,
        "order": 2,
    },
    {
        "slug": "pro",
        "name": "Pro",
        "tagline": "For growth teams scaling across channels.",
        "price_cents": 4900,
        "interval": "month",
        "features": [
            "Unlimited strategies",
            "AI chatbot (unlimited)",
            "Priority recommendations engine",
            "Premium templates and playbooks",
            "Priority support",
        ],
        "is_recommended": True,
        "order": 3,
    },
    {
        "slug": "enterprise",
        "name": "Enterprise",
        "tagline": "For agencies and multi-brand marketing teams.",
        "price_cents": 19900,
        "interval": "month",
        "features": [
            "Everything in Pro",
            "Dedicated strategist",
            "Custom integrations",
            "SSO & advanced permissions",
            "SLA and onboarding",
        ],
        "is_recommended": False,
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Seed marketing solutions and pricing plans."

    @transaction.atomic
    def handle(self, *args, **options):
        solutions_created = 0
        solutions_updated = 0
        for idx, data in enumerate(MARKETING_SOLUTIONS):
            defaults = {
                "title": str(data["title"]),
                "tagline": str(data["tagline"]),
                "icon": data["icon"],
                "overview": str(data["overview"]),
                "benefits": [str(b) for b in data["benefits"]],
                "process": [str(p) for p in data["process"]],
                "use_cases": [str(u) for u in data["use_cases"]],
                "case_study": str(data["case_study"]),
                "is_active": True,
                "order": idx,
            }
            obj, created = MarketingSolution.objects.update_or_create(
                slug=data["slug"], defaults=defaults
            )
            if created:
                solutions_created += 1
            else:
                solutions_updated += 1

        plans_created = 0
        plans_updated = 0
        for data in PRICING_PLANS:
            obj, created = PricingPlan.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                plans_created += 1
            else:
                plans_updated += 1

        services_created = 0
        services_updated = 0
        for data in SERVICES:
            obj, created = Service.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                services_created += 1
            else:
                services_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Solutions: {solutions_created} created, {solutions_updated} updated. "
                f"Plans: {plans_created} created, {plans_updated} updated. "
                f"Services: {services_created} created, {services_updated} updated."
            )
        )
