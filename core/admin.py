from django.contrib import admin
from django.http import HttpRequest

from core.models import ContactRequest, NewsletterSubscription, SiteContact


@admin.register(SiteContact)
class SiteContactAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Контактна інформація', {
            'fields': ('email', 'phone'),
        }),
        ('Соціальні мережі', {
            'fields': ('instagram_url', 'facebook_url'),
        }),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not SiteContact.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """Перенаправляємо зі списку одразу на форму редагування."""
        obj = SiteContact.load()
        return self.changeform_view(request, object_id=str(obj.pk), extra_context=extra_context)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_editable = ('is_processed',)
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at')
    ordering = ('-created_at',)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    readonly_fields = ('email', 'subscribed_at')
    ordering = ('-subscribed_at',)
