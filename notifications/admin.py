from django.contrib import admin
from .models import Notification, NotificationPreference, PushDevice


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = [
        'recipient', 'type', 'title',
        'is_read', 'is_sent_ws', 'is_sent_email', 'created_at'
    ]
    list_filter   = ['type', 'is_read', 'is_sent_ws', 'is_sent_email']
    search_fields = ['recipient__email', 'recipient__full_name', 'title']
    readonly_fields = ['created_at', 'read_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display  = ['user', 'channel', 'new_interest',
                     'interest_accepted', 'new_message']
    list_filter   = ['channel']
    search_fields = ['user__email']


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    list_display  = ['user', 'platform', 'device_name', 'is_active', 'registered_at']
    list_filter   = ['platform', 'is_active']