"""Create profile + company records automatically for every user."""
from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompanyProfile, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profiles(sender, instance, created, **kwargs):
    if not created:
        return
    UserProfile.objects.get_or_create(user=instance)
    CompanyProfile.objects.get_or_create(user=instance)
