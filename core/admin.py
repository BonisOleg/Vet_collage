from django.contrib import admin

from core.models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_editable = ('is_processed',)
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at')
    ordering = ('-created_at',)
