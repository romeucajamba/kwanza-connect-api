from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import RoomEntity, RoomMemberEntity, MessageEntity, MessageReadEntity, MessageReactionEntity, RoomEventEntity
import uuid

class IChatRepository(ABC):
    
    @abstractmethod
    def save_room(self, room: RoomEntity) -> RoomEntity:
        pass

    @abstractmethod
    def get_room_by_id(self, room_id: uuid.UUID) -> Optional[RoomEntity]:
        pass

    @abstractmethod
    def list_user_rooms(self, user_id: uuid.UUID) -> List[RoomEntity]:
        pass

    @abstractmethod
    def save_member(self, member: RoomMemberEntity) -> RoomMemberEntity:
        pass

    @abstractmethod
    def get_member_by_room_and_user(self, room_id: uuid.UUID, user_id: uuid.UUID) -> Optional[RoomMemberEntity]:
        pass

    @abstractmethod
    def list_room_members(self, room_id: uuid.UUID) -> List[RoomMemberEntity]:
        pass

    @abstractmethod
    def save_message(self, message: MessageEntity) -> MessageEntity:
        pass

    @abstractmethod
    def get_message_by_id(self, message_id: uuid.UUID) -> Optional[MessageEntity]:
        pass

    @abstractmethod
    def list_room_messages(self, room_id: uuid.UUID, limit: int = 50, before: Optional[uuid.UUID] = None) -> List[MessageEntity]:
        pass

    @abstractmethod
    def save_read(self, read: MessageReadEntity) -> MessageReadEntity:
        pass

    @abstractmethod
    def save_reaction(self, reaction: MessageReactionEntity) -> MessageReactionEntity:
        pass

    @abstractmethod
    def delete_reaction(self, message_id: uuid.UUID, user_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    def save_event(self, event: RoomEventEntity) -> RoomEventEntity:
        pass

    @abstractmethod
    def list_room_events(self, room_id: uuid.UUID) -> List[RoomEventEntity]:
        pass

    @abstractmethod
    def get_unread_count_for_user(self, room_id: uuid.UUID, user_id: uuid.UUID) -> int:
        pass
