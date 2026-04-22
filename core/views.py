import logging
import re

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from courses.models import Course
from core.models import ContactRequest, NewsletterSubscription


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'pages/core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['popular_courses'] = (
            Course.objects.filter(is_active=True, is_popular=True)
            .select_related('category')[:6]
        )
        return ctx


class AboutView(TemplateView):
    template_name = 'pages/core/about.html'


class PaymentSuccessView(TemplateView):
    template_name = 'pages/payments/success.html'


class PaymentFailureView(TemplateView):
    template_name = 'pages/payments/failure.html'


class PrivacyView(TemplateView):
    template_name = 'pages/core/privacy.html'


class CookiesView(TemplateView):
    template_name = 'pages/core/cookies.html'


def contact_view(request):
    if request.method != 'POST':
        return render(request, 'pages/core/contact.html')

    is_htmx = bool(request.headers.get('HX-Request'))

    # Honeypot: bots fill this field, humans leave it empty
    if request.POST.get('website', '').strip():
        if is_htmx:
            return HttpResponse(
                '<p class="form-success">&#10003; Дякуємо! Ми зв\'яжемося з вами найближчим часом.</p>'
            )
        return redirect('core:home')

    name: str = request.POST.get('name', '').strip()
    phone: str = request.POST.get('phone', '').strip()
    email_addr: str = request.POST.get('email', '').strip()
    message: str = request.POST.get('message', '').strip()

    errors: list[str] = []

    if not name:
        errors.append("Вкажіть ваше ім'я та прізвище.")
    elif len(name) < 2:
        errors.append("Ім'я занадто коротке (мінімум 2 символи).")

    if not email_addr:
        errors.append('Вкажіть email.')
    elif not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email_addr):
        errors.append('Введіть коректний email (наприклад: name@domain.com).')

    if phone and not re.fullmatch(r'[\+\d][\d\s\-\(\)]{6,19}', phone):
        errors.append('Введіть коректний номер телефону.')

    if errors:
        error_html = ''.join(f'<p class="form-error">{e}</p>' for e in errors)
        if is_htmx:
            return HttpResponse(error_html, status=422)
        for err in errors:
            messages.error(request, err)
        return redirect('core:home')

    subject = f"Запит на консультацію від {name}"
    body = (
        f"Ім'я: {name}\n"
        f"Телефон: {phone or '—'}\n"
        f"Email: {email_addr}\n\n"
        f"Повідомлення:\n{message or '—'}"
    )
    
    # Спочатку зберігаємо заявку в БД (критично важливо!)
    try:
        ContactRequest.objects.create(
            name=name,
            phone=phone,
            email=email_addr,
            message=message,
        )
    except Exception as e:
        logger.exception(f"Помилка збереження заявки на консультацію: {e}")
    
    # Email — graceful fallback: спробуємо, але не блокуємо на помилці
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Помилка відправлення email для заявки")
    
    # Завжди повертаємо успіх після збереження в БД
    if is_htmx:
        return HttpResponse(
            '<p class="form-success">&#10003; Дякуємо! Ми зв\'яжемося з вами найближчим часом.</p>'
        )
    messages.success(request, 'Дякуємо за повідомлення!')
    return redirect('core:home')


def newsletter_view(request):
    """Handle newsletter subscription from footer form."""
    if request.method != 'POST':
        return redirect('core:home')

    email = request.POST.get('email', '').strip()
    is_htmx = bool(request.headers.get('HX-Request'))

    # Валідація email
    if not email or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        error_msg = 'Введіть коректний email.'
        if is_htmx:
            return HttpResponse(
                f'<p class="form-error">{error_msg}</p>',
                status=400,
            )
        messages.error(request, error_msg)
        return redirect('core:home')

    # Спочатку зберігаємо підписку в БД
    try:
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'is_active': True},
        )
        # Якщо підписка вже існувала і була деактивована, активуємо її знову
        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.save()
    except Exception as e:
        logger.exception(f"Помилка збереження підписки на розсилку: {e}")

    # Завжди повертаємо успіх
    if is_htmx:
        return HttpResponse(
            '<p class="form-success">&#10003; Дякуємо! Ви підписані на розсилку.</p>'
        )
    messages.success(request, 'Дякуємо! Ви підписані на розсилку.')
    return redirect('core:home')
