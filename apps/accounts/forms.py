"""Authentication and profile forms."""
from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CompanyProfile, UserProfile

User = get_user_model()


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=60, required=False)
    last_name = forms.CharField(max_length=60, required=False)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_("Confirm password"))

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("An account with this email already exists."))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Passwords do not match."))
        if p1:
            try:
                validate_password(p1)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self) -> "User":
        user = User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
            is_active=True,
            is_email_verified=False,
        )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise ValidationError(_("Invalid email or password."))
            self.user = user
        return cleaned


class VerifyEmailForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=6, min_length=6)
    password1 = forms.CharField(widget=forms.PasswordInput, label=_("New password"))
    password2 = forms.CharField(widget=forms.PasswordInput, label=_("Confirm new password"))

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Passwords do not match."))
        if p1:
            try:
                validate_password(p1)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=60, required=False)
    last_name = forms.CharField(max_length=60, required=False)

    class Meta:
        model = UserProfile
        fields = ["avatar", "phone", "bio", "preferred_language", "preferred_theme", "marketing_opt_in"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit: bool = True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data.get("first_name", user.first_name)
        user.last_name = self.cleaned_data.get("last_name", user.last_name)
        if commit:
            user.save(update_fields=["first_name", "last_name"])
        return profile


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ["name", "industry", "size", "website", "country", "description"]
