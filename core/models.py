from django.db import models


class ContactRequest(models.Model):
    """Заявка на консультацію від відвідувача."""
    
    name = models.CharField(max_length=200, verbose_name='Ім\'я та прізвище')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(blank=True, verbose_name='Повідомлення')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    is_processed = models.BooleanField(default=False, verbose_name='Обробленої')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка на консультацію'
        verbose_name_plural = 'Заявки на консультацію'

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"


class NewsletterSubscription(models.Model):
    """Підписка на email-розсилку."""
    
    email = models.EmailField(unique=True, verbose_name='Email')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата підписки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Підписка на розсилку'
        verbose_name_plural = 'Підписки на розсилку'

    def __str__(self) -> str:
        status = "✓ активна" if self.is_active else "✗ деактивована"
        return f"{self.email} ({status})"
