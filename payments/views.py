from __future__ import annotations

import json
import logging

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Order
from .services import StripeService

logger = logging.getLogger(__name__)


@login_required
@require_POST
def create_checkout_view(request: HttpRequest) -> HttpResponse:
    order_type = request.POST.get('order_type', '')
    item_id = request.POST.get('item_id', '')

    if order_type not in ('course', 'webinar', 'membership'):
        return JsonResponse({'error': 'Invalid order type'}, status=400)

    try:
        item_id_int = int(item_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid item ID'}, status=400)

    item_title, amount = _resolve_item(order_type, item_id_int)
    if amount is None:
        return JsonResponse({'error': 'Item not found'}, status=404)

    order = Order.objects.create(
        user=request.user,
        order_type=order_type,
        item_id=item_id_int,
        item_title=item_title,
        amount=amount,
    )

    success_url = request.build_absolute_uri(
        reverse('core:payment_success') + f'?order_id={order.pk}'
    )
    cancel_url = request.build_absolute_uri(
        reverse('core:payment_failure') + f'?order_id={order.pk}'
    )

    session = StripeService.create_checkout_session(order, success_url, cancel_url)
    if session is None:
        order.status = 'failed'
        order.save(update_fields=['status'])
        return JsonResponse({'error': 'Payment service unavailable'}, status=502)

    return JsonResponse({'checkout_url': session.url})


@csrf_exempt
@require_POST
def stripe_webhook_view(request: HttpRequest) -> HttpResponse:
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    event = StripeService.handle_webhook(payload, sig_header)
    if event is None:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        StripeService.fulfill_order(session)

    return HttpResponse(status=200)


def _resolve_item(order_type: str, item_id: int):
    """Return (title, price) for the given item or (None, None)."""
    if order_type == 'course':
        from courses.models import Course
        try:
            c = Course.objects.get(pk=item_id, is_active=True)
            return c.title, c.price
        except Course.DoesNotExist:
            return None, None

    elif order_type == 'webinar':
        from webinars.models import Webinar
        try:
            w = Webinar.objects.get(pk=item_id, is_active=True)
            return w.title, w.price
        except Webinar.DoesNotExist:
            return None, None

    elif order_type == 'membership':
        from membership.models import MembershipPlan
        try:
            p = MembershipPlan.objects.get(pk=item_id)
            return p.name, p.price
        except MembershipPlan.DoesNotExist:
            return None, None

    return None, None
