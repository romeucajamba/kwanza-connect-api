"""
Use cases do módulo de notificações.
"""
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.utils import timezone
from ..models import Notification, NotificationPreference


class GetUserNotificationsUseCase:
    """Lista as notificações de um utilizador."""
    def execute(self, user, limit: int = 50, offset: int = 0):
        return Notification.objects.filter(recipient=user).select_related('actor').order_by('-created_at')[offset:offset+limit]


class MarkNotificationReadUseCase:
    """Marca uma ou todas as notificações como lidas."""
    def execute(self, user, notification_id: str = None):
        if notification_id:
            try:
                notif = Notification.objects.get(id=notification_id, recipient=user)
                notif.mark_as_read()
            except Notification.DoesNotExist:
                raise NotFound('Notificação não encontrada.')
        else:
            Notification.objects.filter(recipient=user, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )


class UpdateNotificationPreferencesUseCase:
    """Actualiza as preferências de notificação do utilizador."""
    def execute(self, user, data: dict) -> NotificationPreference:
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        for attr, val in data.items():
            if hasattr(prefs, attr):
                setattr(prefs, attr, val)
        prefs.save()
        return prefs
