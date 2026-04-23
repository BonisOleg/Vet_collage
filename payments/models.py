from django.db import models
from django.contrib.auth import get_user_model

from core.currency import CURRENCY_CHOICES, DEFAULT_CURRENCY, get_currency_symbol

User = get_user_model()


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('course', 'Курс'),
        ('webinar', 'Вебінар'),
        ('membership', 'Членство'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('paid', 'Оплачено'),
        ('failed', 'Помилка'),
        ('refunded', 'Повернення'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders',
        verbose_name='Користувач',
    )
    order_type = models.CharField(
        'Тип', max_length=20, choices=ORDER_TYPE_CHOICES,
    )
    item_id = models.PositiveIntegerField('ID товару')
    item_title = models.CharField('Назва товару', max_length=255, blank=True)
    amount = models.DecimalField('Сума', max_digits=10, decimal_places=2)
    currency = models.CharField(
        'Валюта', max_length=3, default=DEFAULT_CURRENCY, choices=CURRENCY_CHOICES,
    )
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    stripe_session_id = models.CharField(
        'Stripe Session ID', max_length=255, blank=True, db_index=True,
    )
    stripe_payment_intent_id = models.CharField(
        'Stripe Payment Intent ID', max_length=255, blank=True,
    )
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'#{self.pk} {self.get_order_type_display()} — {self.item_title}'

    @property
    def currency_symbol(self) -> str:
        return get_currency_symbol(self.currency)
