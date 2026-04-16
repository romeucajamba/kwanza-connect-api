from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import NotificationEntity, NotificationPreferenceEntity, PushDeviceEntity
import uuid

class INotificationRepository(ABC):
    
    @abstractmethod
    def save_notification(self, notification: NotificationEntity) -> NotificationEntity:
        pass

    @abstractmethod
    def get_notification_by_id(self, notification_id: uuid.UUID) -> Optional[NotificationEntity]:
        pass

    @abstractmethod
    def list_user_notifications(self, user_id: uuid.UUID, limit: int = 50, only_unread: bool = False) -> List[NotificationEntity]:
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        pass

    @abstractmethod
    def get_unread_count(self, user_id: uuid.UUID) -> int:
        pass

    @abstractmethod
    def save_preference(self, preference: NotificationPreferenceEntity) -> NotificationPreferenceEntity:
        pass

    @abstractmethod
    def get_preference_by_user(self, user_id: uuid.UUID) -> Optional[NotificationPreferenceEntity]:
        pass

    @abstractmethod
    def save_push_device(self, device: PushDeviceEntity) -> PushDeviceEntity:
        pass

    @abstractmethod
    def list_user_push_devices(self, user_id: uuid.UUID) -> List[PushDeviceEntity]:
        pass

    @abstractmethod
    def delete_push_device(self, token: str) -> None:
        pass
