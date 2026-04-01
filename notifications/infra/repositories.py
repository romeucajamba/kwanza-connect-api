from typing import Optional, List
import uuid
from django.db import transaction
from django.utils import timezone
from .models import (
    Notification as DjangoNotification,
    NotificationPreference as DjangoNotificationPreference,
    PushDevice as DjangoPushDevice
)
from ..domain.entities import (
    NotificationEntity, NotificationPreferenceEntity, PushDeviceEntity
)
from ..domain.interfaces import INotificationRepository

class DjangoNotificationRepository(INotificationRepository):
    
    def _notification_to_entity(self, django_notif: DjangoNotification) -> NotificationEntity:
        return NotificationEntity(
            id=django_notif.id,
            recipient_id=django_notif.recipient_id,
            actor_id=django_notif.actor_id,
            type=django_notif.type,
            title=django_notif.title,
            body=django_notif.body,
            payload=django_notif.payload,
            is_read=django_notif.is_read,
            read_at=django_notif.read_at,
            is_sent_ws=django_notif.is_sent_ws,
            is_sent_email=django_notif.is_sent_email,
            is_sent_push=django_notif.is_sent_push,
            created_at=django_notif.created_at
        )

    def _pref_to_entity(self, django_pref: DjangoNotificationPreference) -> NotificationPreferenceEntity:
        return NotificationPreferenceEntity(
            id=django_pref.id,
            user_id=django_pref.user_id,
            channel=django_pref.channel,
            new_interest=django_pref.new_interest,
            interest_accepted=django_pref.interest_accepted,
            interest_rejected=django_pref.interest_rejected,
            interest_cancelled=django_pref.interest_cancelled,
            offer_expired=django_pref.offer_expired,
            new_message=django_pref.new_message,
            deal_accepted=django_pref.deal_accepted,
            deal_cancelled=django_pref.deal_cancelled,
            rate_alert=django_pref.rate_alert,
            account_verified=django_pref.account_verified,
            system=django_pref.system
        )

    def _push_to_entity(self, django_push: DjangoPushDevice) -> PushDeviceEntity:
        return PushDeviceEntity(
            id=django_push.id,
            user_id=django_push.user_id,
            platform=django_push.platform,
            token=django_push.token,
            device_name=django_push.device_name,
            is_active=django_push.is_active,
            registered_at=django_push.registered_at,
            last_used_at=django_push.last_used_at
        )

    def save_notification(self, notification: NotificationEntity) -> NotificationEntity:
        django_notif, created = DjangoNotification.objects.update_or_create(
            id=notification.id,
            defaults={
                'recipient_id': notification.recipient_id,
                'actor_id': notification.actor_id,
                'type': notification.type,
                'title': notification.title,
                'body': notification.body,
                'payload': notification.payload,
                'is_read': notification.is_read,
                'read_at': notification.read_at,
                'is_sent_ws': notification.is_sent_ws,
                'is_sent_email': notification.is_sent_email,
                'is_sent_push': notification.is_sent_push,
            }
        )
        return self._notification_to_entity(django_notif)

    def get_notification_by_id(self, notification_id: uuid.UUID) -> Optional[NotificationEntity]:
        try:
            return self._notification_to_entity(DjangoNotification.objects.get(id=notification_id))
        except DjangoNotification.DoesNotExist:
            return None

    def list_user_notifications(self, user_id: uuid.UUID, limit: int = 50, only_unread: bool = False) -> List[NotificationEntity]:
        qs = DjangoNotification.objects.filter(recipient_id=user_id)
        if only_unread:
            qs = qs.filter(is_read=False)
        notifications = qs.order_by('-created_at')[:limit]
        return [self._notification_to_entity(n) for n in notifications]

    def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        return DjangoNotification.objects.filter(recipient_id=user_id, is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )

    def save_preference(self, preference: NotificationPreferenceEntity) -> NotificationPreferenceEntity:
        # We use user_id as the lookup for preference
        django_pref, created = DjangoNotificationPreference.objects.update_or_create(
            user_id=preference.user_id,
            defaults={
                'channel': preference.channel,
                'new_interest': preference.new_interest,
                'interest_accepted': preference.interest_accepted,
                'interest_rejected': preference.interest_rejected,
                'interest_cancelled': preference.interest_cancelled,
                'offer_expired': preference.offer_expired,
                'new_message': preference.new_message,
                'deal_accepted': preference.deal_accepted,
                'deal_cancelled': preference.deal_cancelled,
                'rate_alert': preference.rate_alert,
                'account_verified': preference.account_verified,
                'system': preference.system,
            }
        )
        return self._pref_to_entity(django_pref)

    def get_preference_by_user(self, user_id: uuid.UUID) -> Optional[NotificationPreferenceEntity]:
        try:
            return self._pref_to_entity(DjangoNotificationPreference.objects.get(user_id=user_id))
        except DjangoNotificationPreference.DoesNotExist:
            return None

    def save_push_device(self, device: PushDeviceEntity) -> PushDeviceEntity:
        django_push, created = DjangoPushDevice.objects.update_or_create(
            token=device.token,
            defaults={
                'user_id': device.user_id,
                'platform': device.platform,
                'device_name': device.device_name,
                'is_active': device.is_active,
                'last_used_at': device.last_used_at,
            }
        )
        return self._push_to_entity(django_push)

    def list_user_push_devices(self, user_id: uuid.UUID) -> List[PushDeviceEntity]:
        devices = DjangoPushDevice.objects.filter(user_id=user_id, is_active=True)
        return [self._push_to_entity(d) for d in devices]

    def delete_push_device(self, token: str) -> None:
        DjangoPushDevice.objects.filter(token=token).delete()
