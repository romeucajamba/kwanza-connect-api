from typing import Optional, List
import uuid
from django.db import transaction
from django.utils import timezone
from ..models import (
    Room as DjangoRoom,
    RoomMember as DjangoRoomMember,
    Message as DjangoMessage,
    MessageRead as DjangoMessageRead,
    MessageReaction as DjangoMessageReaction,
    RoomEvent as DjangoRoomEvent
)
from ..domain.entities import (
    RoomEntity, RoomMemberEntity, MessageEntity, 
    MessageReadEntity, MessageReactionEntity, RoomEventEntity
)
from ..domain.interfaces import IChatRepository

class DjangoChatRepository(IChatRepository):
    
    def _room_to_entity(self, django_room: DjangoRoom) -> RoomEntity:
        return RoomEntity(
            id=django_room.id,
            offer_id=django_room.offer_id,
            room_type=django_room.room_type,
            status=django_room.status,
            created_at=django_room.created_at,
            closed_at=django_room.closed_at,
            other_user=getattr(django_room, 'other_user_data', None)
        )

    def _member_to_entity(self, django_member: DjangoRoomMember) -> RoomMemberEntity:
        return RoomMemberEntity(
            id=django_member.id,
            room_id=django_member.room_id,
            user_id=django_member.user_id,
            is_admin=django_member.is_admin,
            joined_at=django_member.joined_at,
            last_read_at=django_member.last_read_at
        )

    def _message_to_entity(self, django_message: DjangoMessage) -> MessageEntity:
        return MessageEntity(
            id=django_message.id,
            room_id=django_message.room_id,
            sender_id=django_message.sender_id,
            msg_type=django_message.msg_type,
            content=django_message.content,
            file=django_message.file.url if django_message.file else None,
            file_name=django_message.file_name,
            file_size=django_message.file_size,
            reply_to_id=django_message.reply_to_id,
            is_deleted=django_message.is_deleted,
            is_edited=django_message.is_edited,
            created_at=django_message.created_at,
            edited_at=django_message.edited_at
        )

    def save_room(self, room: RoomEntity) -> RoomEntity:
        django_room, created = DjangoRoom.objects.update_or_create(
            id=room.id,
            defaults={
                'offer_id': room.offer_id,
                'room_type': room.room_type,
                'status': room.status,
                'closed_at': room.closed_at,
            }
        )
        return self._room_to_entity(django_room)

    def get_room_by_id(self, room_id: uuid.UUID) -> Optional[RoomEntity]:
        try:
            return self._room_to_entity(DjangoRoom.objects.get(id=room_id))
        except DjangoRoom.DoesNotExist:
            return None

    def list_user_rooms(self, user_id: uuid.UUID) -> List[RoomEntity]:
        # Busca todas as salas do utilizador
        rooms = DjangoRoom.objects.filter(members__user_id=user_id).select_related('offer')
        
        entities = []
        for r in rooms:
            # Identifica o outro membro
            other_member = DjangoRoomMember.objects.filter(room=r).exclude(user_id=user_id).select_related('user').first()
            if other_member and other_member.user:
                r.other_user_data = {
                    "id": str(other_member.user.id),
                    "full_name": other_member.user.full_name,
                    "avatar": other_member.user.avatar.url if other_member.user.avatar else None,
                }
            entities.append(self._room_to_entity(r))
        return entities

    def save_member(self, member: RoomMemberEntity) -> RoomMemberEntity:
        django_member, created = DjangoRoomMember.objects.update_or_create(
            id=member.id,
            defaults={
                'room_id': member.room_id,
                'user_id': member.user_id,
                'is_admin': member.is_admin,
                'last_read_at': member.last_read_at,
            }
        )
        return self._member_to_entity(django_member)

    def get_member_by_room_and_user(self, room_id: uuid.UUID, user_id: uuid.UUID) -> Optional[RoomMemberEntity]:
        try:
            return self._member_to_entity(DjangoRoomMember.objects.get(room_id=room_id, user_id=user_id))
        except DjangoRoomMember.DoesNotExist:
            return None

    def list_room_members(self, room_id: uuid.UUID) -> List[RoomMemberEntity]:
        members = DjangoRoomMember.objects.filter(room_id=room_id).select_related('user')
        return [self._member_to_entity(m) for m in members]

    def save_message(self, message: MessageEntity) -> MessageEntity:
        django_message, created = DjangoMessage.objects.update_or_create(
            id=message.id,
            defaults={
                'room_id': message.room_id,
                'sender_id': message.sender_id,
                'msg_type': message.msg_type,
                'content': message.content,
                'file_name': message.file_name,
                'file_size': message.file_size,
                'reply_to_id': message.reply_to_id,
                'is_deleted': message.is_deleted,
                'is_edited': message.is_edited,
            }
        )
        return self._message_to_entity(django_message)

    def get_message_by_id(self, message_id: uuid.UUID) -> Optional[MessageEntity]:
        try:
            return self._message_to_entity(DjangoMessage.objects.get(id=message_id))
        except DjangoMessage.DoesNotExist:
            return None

    def list_room_messages(self, room_id: uuid.UUID, limit: int = 50, before: Optional[uuid.UUID] = None) -> List[MessageEntity]:
        qs = DjangoMessage.objects.filter(room_id=room_id).select_related('sender')
        if before:
             try:
                 before_msg = DjangoMessage.objects.get(id=before)
                 qs = qs.filter(created_at__lt=before_msg.created_at)
             except DjangoMessage.DoesNotExist:
                 pass
        messages = qs.order_by('-created_at')[:limit]
        return [self._message_to_entity(m) for m in reversed(messages)]

    def save_read(self, read: MessageReadEntity) -> MessageReadEntity:
        django_read, created = DjangoMessageRead.objects.update_or_create(
            id=read.id,
            defaults={
                'message_id': read.message_id,
                'user_id': read.user_id,
                'read_at': read.read_at,
            }
        )
        return MessageReadEntity(
            id=django_read.id,
            message_id=django_read.message_id,
            user_id=django_read.user_id,
            read_at=django_read.read_at
        )

    def save_reaction(self, reaction: MessageReactionEntity) -> MessageReactionEntity:
        django_reaction, created = DjangoMessageReaction.objects.update_or_create(
            id=reaction.id,
            defaults={
                'message_id': reaction.message_id,
                'user_id': reaction.user_id,
                'emoji': reaction.emoji,
            }
        )
        return MessageReactionEntity(
            id=django_reaction.id,
            message_id=django_reaction.message_id,
            user_id=django_reaction.user_id,
            emoji=django_reaction.emoji,
            created_at=django_reaction.created_at
        )

    def delete_reaction(self, message_id: uuid.UUID, user_id: uuid.UUID) -> None:
        DjangoMessageReaction.objects.filter(message_id=message_id, user_id=user_id).delete()

    def save_event(self, event: RoomEventEntity) -> RoomEventEntity:
        django_event, created = DjangoRoomEvent.objects.update_or_create(
            id=event.id,
            defaults={
                'room_id': event.room_id,
                'actor_id': event.actor_id,
                'event_type': event.event_type,
                'payload': event.payload,
            }
        )
        return RoomEventEntity(
            id=django_event.id,
            room_id=django_event.room_id,
            actor_id=django_event.actor_id,
            event_type=django_event.event_type,
            payload=django_event.payload,
            created_at=django_event.created_at
        )

    def list_room_events(self, room_id: uuid.UUID) -> List[RoomEventEntity]:
        events = DjangoRoomEvent.objects.filter(room_id=room_id).order_by('created_at')
        return [RoomEventEntity(
            id=e.id, room_id=e.room_id, actor_id=e.actor_id, 
            event_type=e.event_type, payload=e.payload, created_at=e.created_at
        ) for e in events]

    def get_unread_count_for_user(self, room_id: uuid.UUID, user_id: uuid.UUID) -> int:
        last_read = DjangoRoomMember.objects.filter(room_id=room_id, user_id=user_id).values_list('last_read_at', flat=True).first()
        qs = DjangoMessage.objects.filter(room_id=room_id).exclude(sender_id=user_id).filter(is_deleted=False)
        if last_read:
            qs = qs.filter(created_at__gt=last_read)
        return qs.count()
