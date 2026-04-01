"""Contratos do módulo chat."""
from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import RoomEntity, MessageEntity


class IRoomRepository(ABC):

    @abstractmethod
    def get_by_id(self, room_id: str) -> Optional[RoomEntity]:
        ...

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[RoomEntity]:
        ...

    @abstractmethod
    def get_unread_count(self, room_id: str, user_id: str) -> int:
        ...

    @abstractmethod
    def mark_as_read(self, room_id: str, user_id: str) -> None:
        ...


class IMessageRepository(ABC):

    @abstractmethod
    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        ...

    @abstractmethod
    def list_by_room(self, room_id: str, limit: int = 50, offset: int = 0) -> List[MessageEntity]:
        ...

    @abstractmethod
    def create(self, **data) -> MessageEntity:
        ...

    @abstractmethod
    def soft_delete(self, message_id: str) -> None:
        ...
