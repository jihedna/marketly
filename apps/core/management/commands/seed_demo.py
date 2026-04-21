"""Seed marketing solutions and pricing plans into the database."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.billing.models import PricingPlan
from apps.solutions.catalog import MARKETING_SOLUTIONS
from apps.solutions.models import MarketingSolution

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

        self.stdout.write(
            self.style.SUCCESS(
                f"Solutions: {solutions_created} created, {solutions_updated} updated. "
                f"Plans: {plans_created} created, {plans_updated} updated."
            )
        )
