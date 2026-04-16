"""
Serializers do módulo chat.
"""
from rest_framework import serializers
from ..models import Room, Message, RoomMember, MessageRead, MessageReaction
from users.infra.serializers import PublicUserSerializer


class RoomMemberSerializer(serializers.Serializer):
    id           = serializers.UUIDField(read_only=True)
    user         = PublicUserSerializer(read_only=True)
    is_admin     = serializers.BooleanField(read_only=True)
    joined_at    = serializers.DateTimeField(read_only=True)
    last_read_at = serializers.DateTimeField(read_only=True)


class MessageSerializer(serializers.Serializer):
    id         = serializers.UUIDField(read_only=True)
    room       = serializers.UUIDField(source='room_id', read_only=True)
    sender     = PublicUserSerializer(read_only=True)
    reply_to   = serializers.UUIDField(source='reply_to_id', read_only=True, allow_null=True)
    msg_type   = serializers.CharField(read_only=True)
    content    = serializers.CharField(read_only=True)
    file       = serializers.URLField(read_only=True, allow_null=True)
    file_url   = serializers.URLField(source='file', read_only=True, allow_null=True)
    file_name  = serializers.CharField(read_only=True)
    file_size  = serializers.IntegerField(read_only=True, allow_null=True)
    is_deleted = serializers.BooleanField(read_only=True)
    is_edited  = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    edited_at  = serializers.DateTimeField(read_only=True, allow_null=True)



class RoomSerializer(serializers.Serializer):
    id           = serializers.UUIDField(read_only=True)
    offer        = serializers.UUIDField(source='offer_id', read_only=True, allow_null=True)
    room_type    = serializers.CharField(read_only=True)
    status       = serializers.CharField(read_only=True)
    members      = RoomMemberSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True, allow_null=True)
    unread_count = serializers.SerializerMethodField()
    created_at   = serializers.DateTimeField(read_only=True)
    closed_at    = serializers.DateTimeField(read_only=True, allow_null=True)
    
    # Adicional para resumo na lista
    other_user   = serializers.JSONField(read_only=True, allow_null=True)


    def get_unread_count(self, obj):
        # Support for Entity
        if hasattr(obj, 'unread_count'):
            return obj.unread_count
            
        # Support for Model
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(obj, 'unread_count_for'):
            return obj.unread_count_for(request.user)
        return 0



class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Message
        fields = ['content', 'reply_to', 'msg_type', 'file']

    def validate(self, data):
        if not data.get('content') and not data.get('file'):
            raise serializers.ValidationError('A mensagem deve ter conteúdo ou um ficheiro.')
        return data


class MessageReactionSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model  = MessageReaction
        fields = ['id', 'message', 'user', 'emoji', 'created_at']
