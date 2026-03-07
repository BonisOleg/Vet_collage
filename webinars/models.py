from django.db import models
from django.utils.text import slugify


class Webinar(models.Model):
    title = models.CharField('Назва', max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис')
    cover = models.ImageField('Обкладинка', upload_to='webinars/covers/', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    date = models.DateTimeField('Дата проведення', null=True, blank=True)
    duration_min = models.PositiveIntegerField('Тривалість (хв)', default=60)
    is_active = models.BooleanField('Активний', default=True)
    requires_membership = models.BooleanField('Тільки для членів', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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
