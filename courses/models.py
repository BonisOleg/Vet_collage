from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Початківець'),
        ('intermediate', 'Середній'),
        ('advanced', 'Просунутий'),
    ]

    title = models.CharField('Назва', max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    description = models.TextField('Опис')
    cover = models.ImageField('Обкладинка', upload_to='courses/covers/', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    duration_hours = models.PositiveIntegerField('Тривалість (год)', default=0)
    level = models.CharField('Рівень', max_length=20, choices=LEVEL_CHOICES, default='beginner')
    is_active = models.BooleanField('Активний', default=True)
    is_popular = models.BooleanField('Популярний', default=False)
    requires_membership = models.BooleanField('Тільки для членів', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
