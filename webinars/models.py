from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Webinar(models.Model):
    AUDIENCE_CHOICES = [
        ('owners', 'Для власників'),
        ('experts', 'Для експертів'),
    ]

    title = models.CharField('Назва', max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис')
    cover = models.ImageField('Обкладинка', upload_to='webinars/covers/', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        'Стара ціна', max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Ціна до знижки — відображається закресленою поруч із поточною ціною',
    )
    currency = models.CharField('Валюта', max_length=3, default='EUR')
    date = models.DateTimeField('Дата проведення', null=True, blank=True)
    duration_min = models.PositiveIntegerField('Тривалість (хв)', default=60)
    is_active = models.BooleanField('Активний', default=True)
    is_free = models.BooleanField('Безкоштовний', default=False)
    requires_membership = models.BooleanField('Тільки для членів', default=False)
    audience = models.CharField(
        'Тематика (аудиторія)',
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default='owners',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    speaker = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='webinars_as_speaker', verbose_name='Спікер',
    )
    bunny_library_id = models.CharField(
        'Bunny Library ID', max_length=100, blank=True,
        help_text='ID бібліотеки Bunny.net Stream',
    )
    bunny_video_id = models.CharField(
        'Bunny Video ID', max_length=100, blank=True,
        help_text='GUID відео-запису вебінару в Bunny.net Stream',
    )
    bunny_embed_url = models.URLField(
        'Посилання для вставки відео (Bunny.net)', max_length=500, blank=True,
        help_text=(
            'Скопіюйте URL-адресу iframe з Bunny.net Stream → Share → Embed. '
            'Якщо заповнено — використовується замість Library ID + Video ID.'
        ),
    )

    class Meta:
        verbose_name = 'Вебінар'
        verbose_name_plural = 'Вебінари'
        ordering = ['-date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def currency_symbol(self) -> str:
        return '€' if self.currency == 'EUR' else 'грн'

    @property
    def has_recording(self) -> bool:
        return bool(self.bunny_embed_url or self.bunny_video_id)


class WebinarRegistration(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='webinar_registrations',
        verbose_name='Користувач',
    )
    webinar = models.ForeignKey(
        Webinar, on_delete=models.CASCADE, related_name='registrations',
        verbose_name='Вебінар',
    )
    created_at = models.DateTimeField('Дата реєстрації', auto_now_add=True)

    class Meta:
        verbose_name = 'Реєстрація на вебінар'
        verbose_name_plural = 'Реєстрації на вебінари'
        unique_together = ['user', 'webinar']

    def __str__(self):
        return f'{self.user} → {self.webinar.title}'
