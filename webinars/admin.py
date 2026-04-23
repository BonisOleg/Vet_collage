from django.contrib import admin
from .models import Webinar, WebinarInstructor, WebinarRegistration


class WebinarInstructorInline(admin.TabularInline):
    model = WebinarInstructor
    extra = 1
    fields = ('order', 'name', 'role', 'bio', 'photo')


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'date', 'price', 'original_price', 'is_free',
        'is_active', 'has_recording', 'registration_count', 'created_at',
    ]
    list_filter = ['is_active', 'is_free', 'requires_membership', 'audience', 'date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 25
    inlines = [WebinarInstructorInline]
    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'description',
                'cover', 'price', 'original_price', 'is_free', 'currency',
            ),
        }),
        ('Розклад', {
            'fields': ('date', 'duration_min'),
        }),
        ('Контент', {
            'fields': ('what_you_learn', 'materials_access_note'),
        }),
        ('Параметри', {
            'fields': ('is_active', 'requires_membership', 'audience'),
        }),
        ('Bunny.net — відео', {
            'fields': ('bunny_embed_url', 'bunny_library_id', 'bunny_video_id'),
            'description': (
                'Для вставки відео достатньо заповнити поле «Посилання для вставки відео». '
                'Library ID та Video ID потрібні лише для токен-аутентифікації.'
            ),
        }),
    )

    def has_recording(self, obj):
        return obj.has_recording
    has_recording.boolean = True
    has_recording.short_description = 'Є запис'

    def registration_count(self, obj):
        return obj.registrations.count()
    registration_count.short_description = 'Реєстрацій'


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'webinar', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__username', 'webinar__title']
    raw_id_fields = ['user', 'webinar']
    date_hierarchy = 'created_at'
