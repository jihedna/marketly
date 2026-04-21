"""Transactional email helpers."""
from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def _send(subject: str, template_base: str, context: dict, recipient: str) -> None:
    text_body = render_to_string(f"emails/{template_base}.txt", context)
    html_body = render_to_string(f"emails/{template_base}.html", context)
    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [recipient])
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


def send_verification_email(user, code: str) -> None:
    _send(
        subject=_("Your Marketly verification code"),
        template_base="verification_code",
        context={"user": user, "code": code, "ttl_minutes": 30, "site_url": settings.SITE_URL},
        recipient=user.email,
    )


def send_password_reset_email(user, code: str) -> None:
    _send(
        subject=_("Your Marketly password reset code"),
        template_base="reset_code",
        context={"user": user, "code": code, "ttl_minutes": 30, "site_url": settings.SITE_URL},
        recipient=user.email,
    )


def send_welcome_email(user) -> None:
    _send(
        subject=_("Welcome to Marketly!"),
        template_base="welcome",
        context={"user": user, "site_url": settings.SITE_URL},
        recipient=user.email,
    )


def send_payment_confirmation_email(user, transaction) -> None:
    _send(
        subject=_("Payment confirmed — thank you!"),
        template_base="payment_confirmation",
        context={"user": user, "transaction": transaction, "site_url": settings.SITE_URL},
        recipient=user.email,
    )
