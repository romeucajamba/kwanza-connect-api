"""
Use cases do módulo de notificações.
Orquestra repositórios e lógica de negócio operando sobre Entidades.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from ..domain.entities import NotificationEntity, NotificationPreferenceEntity
from ..domain.interfaces import INotificationRepository

class GetUserNotificationsUseCase:
    def __init__(self, repository: INotificationRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, limit: int = 50, only_unread: bool = False) -> List[NotificationEntity]:
        return self.repository.list_user_notifications(user_id, limit, only_unread)

class MarkNotificationReadUseCase:
    def __init__(self, repository: INotificationRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, notification_id: Optional[uuid.UUID] = None) -> None:
        if notification_id:
            notif = self.repository.get_notification_by_id(notification_id)
            if not notif or notif.recipient_id != user_id:
                raise NotFound('Notificação não encontrada.')
            
            notif.is_read = True
            notif.read_at = datetime.now()
            self.repository.save_notification(notif)
        else:
            self.repository.mark_all_as_read(user_id)

class UpdateNotificationPreferencesUseCase:
    def __init__(self, repository: INotificationRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, data: dict) -> NotificationPreferenceEntity:
        prefs = self.repository.get_preference_by_user(user_id)
        if not prefs:
            prefs = NotificationPreferenceEntity(id=uuid.uuid4(), user_id=user_id)
        
        # Actualiza campos dinamicamente
        for field, value in data.items():
            if hasattr(prefs, field):
                setattr(prefs, field, value)
        
        return self.repository.save_preference(prefs)

class GetNotificationPreferencesUseCase:
    def __init__(self, repository: INotificationRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID) -> NotificationPreferenceEntity:
        prefs = self.repository.get_preference_by_user(user_id)
        if not prefs:
            prefs = NotificationPreferenceEntity(id=uuid.uuid4(), user_id=user_id)
            return self.repository.save_preference(prefs)
        return prefs
