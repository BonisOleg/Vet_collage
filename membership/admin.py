from django.contrib import admin
from .models import MembershipPlan, UserMembership


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'is_popular', 'order']
    list_editable = ['order', 'is_popular']
    ordering = ['order']


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'is_active']
    list_filter = ['status', 'plan']
    search_fields = ['user__email', 'user__username']
    raw_id_fields = ['user']

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Активне'
