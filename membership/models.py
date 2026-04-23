from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MembershipPlan(models.Model):
    name = models.CharField('Назва', max_length=100)
    price = models.DecimalField('Ціна/міс', max_digits=10, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3, default='EUR')
    description = models.TextField('Опис', blank=True)
    features = models.JSONField('Переваги', default=list)
    is_popular = models.BooleanField('Популярний', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Тарифний план'
        verbose_name_plural = 'Тарифні плани'
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def currency_symbol(self) -> str:
        return '€' if self.currency == 'EUR' else 'грн'


class UserMembership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активне'),
        ('expired', 'Закінчилось'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Членство користувача'
        verbose_name_plural = 'Членства користувачів'

    def __str__(self):
        return f'{self.user.email} — {self.plan}'

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and (self.end_date is None or self.end_date >= timezone.now().date())
