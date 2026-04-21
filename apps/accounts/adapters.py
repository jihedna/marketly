"""Allauth adapters — we only use allauth for social login."""
from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Disallow regular allauth signup/login views — we have our own."""

    def is_open_for_signup(self, request) -> bool:
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.is_email_verified = bool(data.get("email"))
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        # Social providers return verified emails; mark so.
        if user.email:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
        return user
