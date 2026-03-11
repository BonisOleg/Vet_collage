from django.contrib import admin
from .models import Category, Course, Enrollment, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = [
        'title', 'slug', 'bunny_video_id', 'duration_seconds',
        'order', 'is_preview',
    ]
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'price', 'level',
        'is_active', 'is_popular', 'lesson_count', 'created_at',
    ]
    list_filter = ['is_active', 'is_popular', 'level', 'category', 'requires_membership']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'category', 'instructor',
                'description', 'cover', 'price',
            ),
        }),
        ('Параметри', {
            'fields': (
                'duration_hours', 'level', 'is_active',
                'is_popular', 'requires_membership',
            ),
        }),
        ('Навчання', {
            'fields': ('what_you_learn',),
        }),
        ('Bunny.net', {
            'fields': ('bunny_library_id',),
            'classes': ('collapse',),
        }),
    )

    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Уроків'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__username', 'course__title']
    raw_id_fields = ['user', 'course']
    date_hierarchy = 'created_at'
