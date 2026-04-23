from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


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
    subtitle = models.CharField('Підзаголовок', max_length=512, blank=True, default='')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses',
    )
    description = models.TextField('Опис')
    cover = models.ImageField('Обкладинка', upload_to='courses/covers/', blank=True)
    price = models.DecimalField('Ціна', max_digits=10, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3, default='EUR')
    duration_hours = models.PositiveIntegerField('Тривалість (год)', default=0)
    level = models.CharField(
        'Рівень', max_length=20, choices=LEVEL_CHOICES, default='beginner',
    )
    is_active = models.BooleanField('Активний', default=True)
    is_popular = models.BooleanField('Популярний', default=False)
    requires_membership = models.BooleanField('Тільки для членів', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    instructor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='taught_courses', verbose_name='Лектор',
    )
    what_you_learn = models.JSONField(
        'Чому навчитесь', default=list, blank=True,
        help_text='Список пунктів, напр. ["Основи нутріціології", "Розрахунок раціонів"]',
    )
    bunny_library_id = models.CharField(
        'Bunny Library ID', max_length=100, blank=True,
        help_text='ID бібліотеки Bunny.net Stream (якщо відрізняється від глобального)',
    )
    promo_bunny_video_id = models.CharField(
        'Промо-відео (Bunny Video ID)', max_length=100, blank=True,
        help_text='GUID промо-відео курсу в Bunny.net Stream',
    )
    materials_access_note = models.TextField(
        'Умови доступу до матеріалів', default='', blank=True,
    )

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

    @property
    def currency_symbol(self) -> str:
        return '€' if self.currency == 'EUR' else 'грн'

    @property
    def total_duration_seconds(self) -> int:
        return self.lessons.aggregate(total=models.Sum('duration_seconds'))['total'] or 0

    @property
    def lesson_count(self) -> int:
        return self.lessons.count()


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons',
        verbose_name='Курс',
    )
    title = models.CharField('Назва', max_length=255)
    slug = models.SlugField()
    description = models.TextField('Опис', blank=True)
    bunny_video_id = models.CharField(
        'Bunny Video ID', max_length=100, blank=True,
        help_text='GUID відео в Bunny.net Stream',
    )
    duration_seconds = models.PositiveIntegerField('Тривалість (сек)', default=0)
    order = models.PositiveIntegerField('Порядок', default=0)
    module_number = models.PositiveSmallIntegerField('Номер модуля', default=1)
    module_title = models.CharField('Назва модуля', max_length=255, blank=True, default='')
    is_preview = models.BooleanField(
        'Безкоштовний перегляд', default=False,
        help_text='Дозволити перегляд без покупки курсу',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']
        unique_together = ['course', 'slug']

    def __str__(self):
        return f'{self.course.title} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class CourseInstructor(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='instructors',
        verbose_name='Курс',
    )
    name = models.CharField('ПІБ', max_length=255)
    role = models.CharField('Роль/посада', max_length=255, blank=True)
    bio = models.TextField('Біографія', blank=True)
    photo = models.ImageField('Фото', upload_to='instructors/', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Спікер'
        verbose_name_plural = 'Спікери'
        ordering = ['order']

    def __str__(self):
        return f'{self.name} ({self.course.title})'


class Enrollment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments',
        verbose_name='Користувач',
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments',
        verbose_name='Курс',
    )
    created_at = models.DateTimeField('Дата запису', auto_now_add=True)

    class Meta:
        verbose_name = 'Запис на курс'
        verbose_name_plural = 'Записи на курси'
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user} → {self.course.title}'
