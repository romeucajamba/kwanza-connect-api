"""
Serializers do módulo chat.
"""
from rest_framework import serializers
from ..models import Room, Message, RoomMember, MessageRead, MessageReaction
from users.infra.serializers import PublicUserSerializer


class RoomMemberSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model  = RoomMember
        fields = ['id', 'user', 'is_admin', 'joined_at', 'last_read_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)
    # Como agora é URLField, não usamos mais .url
    file_url = serializers.URLField(source='file', read_only=True)

    class Meta:
        model  = Message
        fields = [
            'id', 'room', 'sender', 'reply_to',
            'msg_type', 'content', 'file', 'file_url',
            'file_name', 'file_size', 'is_deleted', 'is_edited',
            'created_at', 'edited_at'
        ]
        read_only_fields = ['id', 'sender', 'is_deleted', 'is_edited', 'created_at', 'edited_at']


class RoomSerializer(serializers.ModelSerializer):
    members = RoomMemberSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model  = Room
        fields = [
            'id', 'offer', 'room_type', 'status',
            'members', 'last_message', 'unread_count',
            'created_at', 'closed_at'
        ]

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
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
