"""Recommendations model."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class Recommendation(models.Model):
    KIND_CHOICES = [
        ("strategy", "Strategy"),
        ("channel", "Channel"),
        ("service", "Service"),
        ("budget", "Budget"),
        ("plan", "Plan"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations"
    )
    project = models.ForeignKey(
        "solutions.CampaignProject",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="recommendations",
    )
    kind = models.CharField(max_length=32, choices=KIND_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.kind}: {self.title}"
