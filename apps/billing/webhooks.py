"""Stripe webhook handling."""
from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.emails import send_payment_confirmation_email

from .models import PaymentTransaction, PricingPlan, Subscription

try:
    import stripe
except Exception:  # pragma: no cover
    stripe = None  # type: ignore


@csrf_exempt
@require_POST
def stripe_webhook(request):
    if not (stripe and settings.STRIPE_SECRET_KEY):
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
    except Exception:  # pragma: no cover - depends on real Stripe payloads
        return HttpResponseBadRequest("Invalid signature")

    etype = event.get("type") if isinstance(event, dict) else event.type
    data = (event.get("data") or {}).get("object") if isinstance(event, dict) else event.data.object

    if etype == "checkout.session.completed" and data:
        metadata = (data.get("metadata") or {}) if isinstance(data, dict) else getattr(data, "metadata", {}) or {}
        txn_id = metadata.get("txn_id")
        plan_slug = metadata.get("plan_slug")
        user_id = metadata.get("user_id")
        txn = PaymentTransaction.objects.filter(pk=txn_id).first() if txn_id else None
        if txn:
            txn.status = "succeeded"
            txn.stripe_session_id = data.get("id", txn.stripe_session_id) if isinstance(data, dict) else txn.stripe_session_id
            txn.save(update_fields=["status", "stripe_session_id"])
            plan = PricingPlan.objects.filter(slug=plan_slug).first()
            if plan and user_id:
                Subscription.objects.update_or_create(
                    user_id=user_id,
                    defaults={"plan": plan, "status": "active", "updated_at": timezone.now()},
                )
            send_payment_confirmation_email(txn.user, txn)
    return HttpResponse(status=200)
