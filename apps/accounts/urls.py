from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("forgot-password/", views.PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "reset-password/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
