"""Solutions, campaigns and strategy plans."""
from __future__ import annotations

import json

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class MarketingSolution(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    tagline = models.CharField(max_length=200, blank=True, default="")
    icon = models.CharField(max_length=4, default="✨")
    overview = models.TextField(blank=True, default="")
    benefits = models.JSONField(default=list, blank=True)
    process = models.JSONField(default=list, blank=True)
    use_cases = models.JSONField(default=list, blank=True)
    case_study = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("solutions:detail", args=[self.slug])


class CampaignProject(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("planning", _("Planning")),
        ("active", _("Active")),
        ("completed", _("Completed")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaign_projects"
    )
    solution = models.ForeignKey(
        MarketingSolution, on_delete=models.SET_NULL, blank=True, null=True, related_name="projects"
    )
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="draft")
    company_snapshot = models.JSONField(default=dict, blank=True)
    campaign_details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class StrategyPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strategy_plans"
    )
    project = models.ForeignKey(
        CampaignProject, on_delete=models.CASCADE, related_name="plans", blank=True, null=True
    )
    solution = models.ForeignKey(
        MarketingSolution, on_delete=models.SET_NULL, blank=True, null=True, related_name="plans"
    )
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, default="")
    plan_data = models.JSONField(default=dict, blank=True)
    is_premium_unlocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("solutions:plan_detail", args=[self.pk])

    @property
    def data_pretty(self) -> str:
        return json.dumps(self.plan_data, indent=2, ensure_ascii=False)
