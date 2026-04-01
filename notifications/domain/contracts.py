"""Contratos do módulo de notificações."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from .entities import NotificationEntity, NotificationPreferenceEntity


class INotificationRepository(ABC):

    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional[NotificationEntity]:
        ...

    @abstractmethod
    def list_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[NotificationEntity]:
        ...

    @abstractmethod
    def get_unread_count(self, user_id: str) -> int:
        ...

    @abstractmethod
    def mark_as_read(self, notification_id: str, user_id: str) -> None:
        ...

    @abstractmethod
    def mark_all_as_read(self, user_id: str) -> None:
        ...

    @abstractmethod
    def create(self, **data) -> NotificationEntity:
        ...


class INotificationPreferenceRepository(ABC):

    @abstractmethod
    def get_by_user(self, user_id: str) -> Optional[NotificationPreferenceEntity]:
        ...

    @abstractmethod
    def update(self, user_id: str, **fields) -> NotificationPreferenceEntity:
        ...
        
    @abstractmethod
    def exists_by_user(self, user_id: str) -> bool:
        ...
