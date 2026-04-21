"""Accounts models: custom User, profiles, verification/reset codes."""
from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Email-first custom user model."""

    username = None
    email = models.EmailField(_("email address"), unique=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.email

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.email.split("@")[0]


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [("en", "English"), ("fr", "Français"), ("ar", "العربية")]
    THEME_CHOICES = [("light", _("Light")), ("dark", _("Dark"))]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    preferred_language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default="en")
    preferred_theme = models.CharField(max_length=8, choices=THEME_CHOICES, default="light")
    phone = models.CharField(max_length=32, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    marketing_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Profile({self.user_id})"


class CompanyProfile(models.Model):
    SIZE_CHOICES = [
        ("1-10", _("1-10 employees")),
        ("11-50", _("11-50 employees")),
        ("51-200", _("51-200 employees")),
        ("201-1000", _("201-1000 employees")),
        ("1000+", _("1000+ employees")),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company")
    name = models.CharField(max_length=150, blank=True, default="")
    industry = models.CharField(max_length=100, blank=True, default="")
    size = models.CharField(max_length=32, blank=True, default="", choices=SIZE_CHOICES)
    website = models.URLField(blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name or f"Company({self.user_id})"


def _generate_code(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


class _ExpiringCode(models.Model):
    CODE_TTL = timedelta(minutes=30)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    code = models.CharField(max_length=6, default=_generate_code, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    @property
    def is_expired(self) -> bool:
        return timezone.now() - self.created_at > self.CODE_TTL

    @property
    def is_usable(self) -> bool:
        return self.used_at is None and not self.is_expired

    def consume(self) -> None:
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @classmethod
    def issue_for(cls, user):
        # Invalidate older unused codes
        cls.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        return cls.objects.create(user=user)


class EmailVerificationCode(_ExpiringCode):
    class Meta(_ExpiringCode.Meta):
        verbose_name = _("Email verification code")
        verbose_name_plural = _("Email verification codes")


class PasswordResetCode(_ExpiringCode):
    class Meta(_ExpiringCode.Meta):
        verbose_name = _("Password reset code")
        verbose_name_plural = _("Password reset codes")
