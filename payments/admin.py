from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'order_type', 'item_title', 'amount',
        'currency', 'status', 'created_at',
    ]
    list_filter = ['status', 'order_type', 'created_at']
    search_fields = ['user__email', 'user__username', 'item_title', 'stripe_session_id']
    readonly_fields = [
        'stripe_session_id', 'stripe_payment_intent_id',
        'created_at', 'updated_at',
    ]
    list_per_page = 50
    date_hierarchy = 'created_at'
