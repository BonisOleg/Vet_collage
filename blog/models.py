from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class BlogCategory(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'Всі'),
        ('vets', 'Для ветеринарних лікарів'),
        ('owners', 'Для власників улюбленців'),
    ]

    name = models.CharField('Назва', max_length=100)
    slug = models.SlugField(unique=True)
    audience = models.CharField('Аудиторія', max_length=20, choices=AUDIENCE_CHOICES, default='all')

    class Meta:
        verbose_name = 'Категорія блогу'
        verbose_name_plural = 'Категорії блогу'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    cover = models.ImageField('Обкладинка', upload_to='blog/covers/', blank=True)
    excerpt = models.TextField('Анотація', max_length=300, blank=True)
    content = models.TextField('Текст')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    requires_membership = models.BooleanField('Тільки для членів', default=False)
    is_published = models.BooleanField('Опубліковано', default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Стаття'
        verbose_name_plural = 'Статті'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
