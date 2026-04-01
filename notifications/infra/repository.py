"""
Repositório concreto do módulo de notificações.
"""
from typing import Optional, List
from django.utils import timezone
from ..domain.contracts import INotificationRepository, INotificationPreferenceRepository
from ..domain.entities import NotificationEntity, NotificationPreferenceEntity
from ..models import Notification, NotificationPreference


class NotificationRepository(INotificationRepository):

    def _to_entity(self, notif: Notification) -> NotificationEntity:
        return NotificationEntity(
            id=str(notif.id),
            recipient_id=str(notif.recipient_id),
            actor_id=str(notif.actor_id) if notif.actor_id else None,
            type=notif.type,
            title=notif.title,
            body=notif.body,
            payload=notif.payload,
            is_read=notif.is_read,
            read_at=notif.read_at,
            created_at=notif.created_at
        )

    def get_by_id(self, notification_id: str) -> Optional[NotificationEntity]:
        try:
            return self._to_entity(Notification.objects.get(id=notification_id))
        except Notification.DoesNotExist:
            return None

    def list_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[NotificationEntity]:
        notifs = Notification.objects.filter(recipient_id=user_id).order_by('-created_at')[offset:offset+limit]
        return [self._to_entity(n) for n in notifs]

    def get_unread_count(self, user_id: str) -> int:
        return Notification.objects.filter(recipient_id=user_id, is_read=False).count()

    def mark_as_read(self, notification_id: str, user_id: str) -> None:
        Notification.objects.filter(id=notification_id, recipient_id=user_id).update(
            is_read=True, read_at=timezone.now()
        )

    def mark_all_as_read(self, user_id: str) -> None:
        Notification.objects.filter(recipient_id=user_id, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

    def create(self, **data) -> NotificationEntity:
        notif = Notification.objects.create(**data)
        return self._to_entity(notif)


class NotificationPreferenceRepository(INotificationPreferenceRepository):

    def _to_entity(self, prefs: NotificationPreference) -> NotificationPreferenceEntity:
        return NotificationPreferenceEntity(
            user_id=str(prefs.user_id),
            channel=prefs.channel,
            new_interest=prefs.new_interest,
            interest_accepted=prefs.interest_accepted,
            interest_rejected=prefs.interest_rejected,
            interest_cancelled=prefs.interest_cancelled,
            offer_expired=prefs.offer_expired,
            new_message=prefs.new_message,
            deal_accepted=prefs.deal_accepted,
            deal_cancelled=prefs.deal_cancelled,
            rate_alert=prefs.rate_alert,
            account_verified=prefs.account_verified,
            system=prefs.system
        )

    def get_by_user(self, user_id: str) -> Optional[NotificationPreferenceEntity]:
        try:
            return self._to_entity(NotificationPreference.objects.get(user_id=user_id))
        except NotificationPreference.DoesNotExist:
            return None

    def update(self, user_id: str, **fields) -> NotificationPreferenceEntity:
        NotificationPreference.objects.filter(user_id=user_id).update(**fields)
        return self.get_by_user(user_id)

    def exists_by_user(self, user_id: str) -> bool:
        return NotificationPreference.objects.filter(user_id=user_id).exists()
