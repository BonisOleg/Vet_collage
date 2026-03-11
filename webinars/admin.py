from django.contrib import admin
from .models import Webinar, WebinarRegistration


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'date', 'price', 'is_free',
        'is_active', 'has_recording', 'registration_count', 'created_at',
    ]
    list_filter = ['is_active', 'is_free', 'requires_membership', 'date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'speaker', 'description',
                'cover', 'price', 'is_free',
            ),
        }),
        ('Розклад', {
            'fields': ('date', 'duration_min'),
        }),
        ('Параметри', {
            'fields': ('is_active', 'requires_membership'),
        }),
        ('Bunny.net', {
            'fields': ('bunny_library_id', 'bunny_video_id'),
            'classes': ('collapse',),
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
