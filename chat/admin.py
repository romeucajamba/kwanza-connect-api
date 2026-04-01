from django.contrib import admin
from .models import Room, RoomMember, Message, MessageRead, MessageReaction, RoomEvent


class RoomMemberInline(admin.TabularInline):
    model  = RoomMember
    extra  = 0
    readonly_fields = ['joined_at', 'last_read_at']


class MessageInline(admin.TabularInline):
    model          = Message
    extra          = 0
    readonly_fields = ['created_at', 'edited_at']
    fields         = ['sender', 'msg_type', 'content', 'is_deleted', 'created_at']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ['id', 'room_type', 'status', 'offer', 'created_at']
    list_filter   = ['room_type', 'status']
    search_fields = ['id', 'members__user__email']
    inlines       = [RoomMemberInline, MessageInline]
    readonly_fields = ['created_at', 'closed_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['sender', 'room', 'msg_type', 'is_deleted', 'is_edited', 'created_at']
    list_filter   = ['msg_type', 'is_deleted', 'is_edited']
    search_fields = ['sender__email', 'content']
    readonly_fields = ['created_at', 'edited_at']


@admin.register(RoomEvent)
class RoomEventAdmin(admin.ModelAdmin):
    list_display  = ['room', 'event_type', 'actor', 'created_at']
    list_filter   = ['event_type']
    readonly_fields = ['created_at']