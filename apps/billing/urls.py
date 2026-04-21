from django.urls import path

from . import views

urlpatterns = [
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("checkout/<slug:slug>/", views.CheckoutView.as_view(), name="checkout"),
    path("success/", views.checkout_success, name="success"),
    path("cancel/", views.checkout_cancel, name="cancel"),
]
