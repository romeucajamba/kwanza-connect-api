"""
Repositório concreto do módulo chat.
"""
from typing import Optional, List
from django.db.models import Q
from ..domain.contracts import IRoomRepository, IMessageRepository
from ..domain.entities import RoomEntity, MessageEntity
from ..models import Room, Message, RoomMember


class RoomRepository(IRoomRepository):

    def _to_entity(self, room: Room) -> RoomEntity:
        return RoomEntity(
            id=str(room.id),
            offer_id=str(room.offer_id) if room.offer_id else None,
            room_type=room.room_type,
            status=room.status,
            created_at=room.created_at,
            closed_at=room.closed_at
        )

    def get_by_id(self, room_id: str) -> Optional[RoomEntity]:
        try:
            return self._to_entity(Room.objects.get(id=room_id))
        except Room.DoesNotExist:
            return None

    def list_by_user(self, user_id: str) -> List[RoomEntity]:
        rooms = Room.objects.filter(members__user_id=user_id).distinct()
        return [self._to_entity(r) for r in rooms]

    def get_unread_count(self, room_id: str, user_id: str) -> int:
        try:
            room = Room.objects.get(id=room_id)
            return room.unread_count_for_user_id(user_id)
        except Room.DoesNotExist:
            return 0

    def mark_as_read(self, room_id: str, user_id: str) -> None:
        RoomMember.objects.filter(room_id=room_id, user_id=user_id).update(
            last_read_at=__import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
        )


class MessageRepository(IMessageRepository):

    def _to_entity(self, msg: Message) -> MessageEntity:
        return MessageEntity(
            id=str(msg.id),
            room_id=str(msg.room_id),
            sender_id=str(msg.sender_id) if msg.sender_id else None,
            reply_to_id=str(msg.reply_to_id) if msg.reply_to_id else None,
            msg_type=msg.msg_type,
            content=msg.content,
            file_url=msg.file.url if msg.file else None,
            file_name=msg.file_name,
            file_size=msg.file_size,
            is_deleted=msg.is_deleted,
            is_edited=msg.is_edited,
            created_at=msg.created_at,
            edited_at=msg.edited_at
        )

    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        try:
            return self._to_entity(Message.objects.get(id=message_id))
        except Message.DoesNotExist:
            return None

    def list_by_room(self, room_id: str, limit: int = 50, offset: int = 0) -> List[MessageEntity]:
        messages = Message.objects.filter(room_id=room_id).order_by('-created_at')[offset:offset+limit]
        # Return in chronological order
        return [self._to_entity(m) for m in reversed(list(messages))]

    def create(self, **data) -> MessageEntity:
        msg = Message.objects.create(**data)
        return self._to_entity(msg)

    def soft_delete(self, message_id: str) -> None:
        try:
            msg = Message.objects.get(id=message_id)
            msg.soft_delete()
        except Message.DoesNotExist:
            pass
