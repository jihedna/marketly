"""Pricing + Stripe checkout views."""
from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View

from apps.accounts.emails import send_payment_confirmation_email

from .models import PaymentTransaction, PricingPlan, Subscription

try:  # Stripe is optional for local dev without keys.
    import stripe
except Exception:  # pragma: no cover
    stripe = None  # type: ignore


class PricingView(View):
    template_name = "billing/pricing.html"

    def get(self, request):
        plans = PricingPlan.objects.filter(is_active=True)
        return render(request, self.template_name, {"plans": plans})


@method_decorator(login_required, name="dispatch")
class CheckoutView(View):
    template_name = "billing/checkout.html"

    def get(self, request, slug: str):
        plan = get_object_or_404(PricingPlan, slug=slug, is_active=True)
        stripe_configured = bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLIC_KEY)
        return render(
            request,
            self.template_name,
            {"plan": plan, "stripe_configured": stripe_configured},
        )

    def post(self, request, slug: str):
        plan = get_object_or_404(PricingPlan, slug=slug, is_active=True)
        # Create a transaction record regardless
        txn = PaymentTransaction.objects.create(
            user=request.user,
            plan=plan,
            amount_cents=plan.price_cents,
            currency=plan.currency,
            status="pending",
        )
        success_url = request.build_absolute_uri(
            reverse("billing:success") + f"?txn={txn.id}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("billing:cancel") + f"?txn={txn.id}"
        )

        if plan.price_cents == 0:
            # Free plan — activate immediately.
            txn.status = "succeeded"
            txn.save(update_fields=["status"])
            Subscription.objects.update_or_create(
                user=request.user,
                defaults={"plan": plan, "status": "active"},
            )
            send_payment_confirmation_email(request.user, txn)
            messages.success(request, _("Free plan activated."))
            return redirect(success_url)

        if not (settings.STRIPE_SECRET_KEY and stripe):
            # Simulated checkout for local dev.
            messages.info(
                request,
                _("Stripe is not configured, simulating a successful test payment."),
            )
            txn.status = "succeeded"
            txn.save(update_fields=["status"])
            Subscription.objects.update_or_create(
                user=request.user,
                defaults={"plan": plan, "status": "active"},
            )
            send_payment_confirmation_email(request.user, txn)
            return redirect(success_url)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            mode="subscription" if plan.interval != "once" else "payment",
            line_items=[
                {
                    "price_data": {
                        "currency": plan.currency.lower(),
                        "product_data": {"name": plan.name},
                        "unit_amount": plan.price_cents,
                        **(
                            {"recurring": {"interval": plan.interval}}
                            if plan.interval in ("month", "year")
                            else {}
                        ),
                    },
                    "quantity": 1,
                }
            ],
            customer_email=request.user.email,
            success_url=success_url + "&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={"user_id": str(request.user.id), "plan_slug": plan.slug, "txn_id": str(txn.id)},
        )
        txn.stripe_session_id = session.id
        txn.save(update_fields=["stripe_session_id"])
        return redirect(session.url)


@login_required
def checkout_success(request):
    txn_id = request.GET.get("txn")
    txn = PaymentTransaction.objects.filter(pk=txn_id, user=request.user).first()
    return render(request, "billing/success.html", {"txn": txn})


@login_required
def checkout_cancel(request):
    txn_id = request.GET.get("txn")
    txn = PaymentTransaction.objects.filter(pk=txn_id, user=request.user).first()
    if txn and txn.status == "pending":
        txn.status = "failed"
        txn.save(update_fields=["status"])
    return render(request, "billing/cancel.html", {"txn": txn})
