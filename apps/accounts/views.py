"""Account views: signup, login, logout, verify, password reset."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View

from . import emails
from .forms import (
    CompanyProfileForm,
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    SignupForm,
    UserProfileForm,
    VerifyEmailForm,
)
from .models import EmailVerificationCode, PasswordResetCode

User = get_user_model()


class SignupView(View):
    template_name = "account/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        user = form.save()
        code = EmailVerificationCode.issue_for(user)
        emails.send_verification_email(user, code.code)
        request.session["pending_verification_user_id"] = user.id
        messages.success(
            request, _("Account created! We sent a 6-digit verification code to %(email)s.")
            % {"email": user.email},
        )
        return redirect("accounts:verify_email")


class LoginView(View):
    template_name = "account/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm(request=request)})

    def post(self, request):
        form = LoginForm(request.POST, request=request)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        user = form.user
        if not user.is_email_verified:
            code = EmailVerificationCode.issue_for(user)
            emails.send_verification_email(user, code.code)
            request.session["pending_verification_user_id"] = user.id
            messages.info(
                request,
                _("Please verify your email to continue. A new code was sent to %(email)s.")
                % {"email": user.email},
            )
            return redirect("accounts:verify_email")
        login(request, user)
        # Remember-me: when unchecked, expire the session when the browser
        # closes; when checked, use the default 2-week persistent session.
        remember_me = form.cleaned_data.get("remember_me", False)
        if remember_me:
            request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days
        else:
            request.session.set_expiry(0)  # browser close
        messages.success(request, _("Welcome back, %(name)s!") % {"name": user.display_name})
        next_url = request.GET.get("next") or reverse("dashboard:home")
        return redirect(next_url)


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, _("You have been signed out."))
        return redirect("core:home")

    get = post  # allow GET for simplicity


class VerifyEmailView(View):
    template_name = "account/verify_email.html"

    def _pending_user(self, request):
        uid = request.session.get("pending_verification_user_id")
        if not uid:
            return None
        return User.objects.filter(pk=uid).first()

    def get(self, request):
        user = self._pending_user(request)
        return render(request, self.template_name, {"form": VerifyEmailForm(), "pending_user": user})

    def post(self, request):
        if "resend" in request.POST:
            user = self._pending_user(request)
            if user:
                code = EmailVerificationCode.issue_for(user)
                emails.send_verification_email(user, code.code)
                messages.success(request, _("A new verification code has been sent."))
            return redirect("accounts:verify_email")

        form = VerifyEmailForm(request.POST)
        user = self._pending_user(request)
        if not user:
            messages.error(request, _("No pending verification found. Please sign up or log in again."))
            return redirect("accounts:login")
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "pending_user": user})
        code_value = form.cleaned_data["code"]
        code = (
            EmailVerificationCode.objects.filter(user=user, code=code_value, used_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if not code or not code.is_usable:
            form.add_error("code", _("Invalid or expired code."))
            return render(request, self.template_name, {"form": form, "pending_user": user})
        code.consume()
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        emails.send_welcome_email(user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        request.session.pop("pending_verification_user_id", None)
        messages.success(request, _("Email verified! Welcome to Marketly."))
        return redirect("dashboard:home")


class PasswordResetRequestView(View):
    template_name = "account/password_reset_request.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PasswordResetRequestForm()})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        email = form.cleaned_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            code = PasswordResetCode.issue_for(user)
            emails.send_password_reset_email(user, code.code)
        messages.success(
            request,
            _("If an account exists for %(email)s, a reset code has been sent.") % {"email": email},
        )
        request.session["pending_reset_email"] = email
        return redirect("accounts:password_reset_confirm")


class PasswordResetConfirmView(View):
    template_name = "account/password_reset_confirm.html"

    def get(self, request):
        initial = {"email": request.session.get("pending_reset_email", "")}
        return render(request, self.template_name, {"form": PasswordResetConfirmForm(initial=initial)})

    def post(self, request):
        form = PasswordResetConfirmForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        email = form.cleaned_data["email"]
        code_value = form.cleaned_data["code"]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            form.add_error("email", _("No account matches that email."))
            return render(request, self.template_name, {"form": form})
        code = (
            PasswordResetCode.objects.filter(user=user, code=code_value, used_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if not code or not code.is_usable:
            form.add_error("code", _("Invalid or expired code."))
            return render(request, self.template_name, {"form": form})
        code.consume()
        user.set_password(form.cleaned_data["password1"])
        user.save()
        request.session.pop("pending_reset_email", None)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, _("Password updated. You are now signed in."))
        return redirect("dashboard:home")


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    template_name = "account/profile.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "profile_form": UserProfileForm(instance=request.user.profile),
                "company_form": CompanyProfileForm(instance=request.user.company),
            },
        )

    def post(self, request):
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        company_form = CompanyProfileForm(request.POST, instance=request.user.company)
        if profile_form.is_valid() and company_form.is_valid():
            profile_form.save()
            company_form.save()
            messages.success(request, _("Profile updated."))
            return redirect("accounts:profile")
        return render(
            request, self.template_name, {"profile_form": profile_form, "company_form": company_form}
        )
