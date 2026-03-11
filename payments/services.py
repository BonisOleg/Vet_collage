from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

import stripe
from django.conf import settings
from django.urls import reverse

from .models import Order

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    @staticmethod
    def create_checkout_session(
        order: Order,
        success_url: str,
        cancel_url: str,
    ) -> Optional[stripe.checkout.Session]:
        amount_cents = int(order.amount * 100)
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': order.currency.lower(),
                        'unit_amount': amount_cents,
                        'product_data': {
                            'name': order.item_title or f'{order.get_order_type_display()} #{order.item_id}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(order.pk),
                metadata={
                    'order_id': str(order.pk),
                    'order_type': order.order_type,
                    'item_id': str(order.item_id),
                },
            )
            order.stripe_session_id = session.id
            order.save(update_fields=['stripe_session_id'])
            return session
        except stripe.error.StripeError:
            logger.exception('Stripe checkout session creation failed for order %s', order.pk)
            return None

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str) -> Optional[stripe.Event]:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET,
            )
            return event
        except (ValueError, stripe.error.SignatureVerificationError):
            logger.exception('Stripe webhook verification failed')
            return None

    @staticmethod
    def fulfill_order(session: stripe.checkout.Session) -> None:
        order_id = session.metadata.get('order_id')
        if not order_id:
            logger.error('No order_id in Stripe session metadata')
            return

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            logger.error('Order %s not found during fulfillment', order_id)
            return

        if order.status == 'paid':
            return

        order.status = 'paid'
        order.stripe_payment_intent_id = session.payment_intent or ''
        order.save(update_fields=['status', 'stripe_payment_intent_id', 'updated_at'])

        if order.order_type == 'course':
            _fulfill_course(order)
        elif order.order_type == 'webinar':
            _fulfill_webinar(order)
        elif order.order_type == 'membership':
            _fulfill_membership(order)


def _fulfill_course(order: Order) -> None:
    from courses.models import Course, Enrollment
    try:
        course = Course.objects.get(pk=order.item_id)
        Enrollment.objects.get_or_create(user=order.user, course=course)
        logger.info('Enrolled user %s in course %s', order.user_id, course.pk)
    except Course.DoesNotExist:
        logger.error('Course %s not found for order %s', order.item_id, order.pk)


def _fulfill_webinar(order: Order) -> None:
    from webinars.models import Webinar, WebinarRegistration
    try:
        webinar = Webinar.objects.get(pk=order.item_id)
        WebinarRegistration.objects.get_or_create(user=order.user, webinar=webinar)
        logger.info('Registered user %s for webinar %s', order.user_id, webinar.pk)
    except Webinar.DoesNotExist:
        logger.error('Webinar %s not found for order %s', order.item_id, order.pk)


def _fulfill_membership(order: Order) -> None:
    from membership.models import MembershipPlan, UserMembership
    from django.utils import timezone
    from datetime import timedelta
    try:
        plan = MembershipPlan.objects.get(pk=order.item_id)
        membership, created = UserMembership.objects.get_or_create(
            user=order.user,
            defaults={
                'plan': plan,
                'status': 'active',
                'end_date': timezone.now().date() + timedelta(days=365),
            },
        )
        if not created:
            membership.plan = plan
            membership.status = 'active'
            membership.end_date = timezone.now().date() + timedelta(days=365)
            membership.save()
        logger.info('Activated membership for user %s, plan %s', order.user_id, plan.pk)
    except MembershipPlan.DoesNotExist:
        logger.error('Plan %s not found for order %s', order.item_id, order.pk)
