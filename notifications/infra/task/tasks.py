from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, notification_id: str):
    """Envia notificação por email se o utilizador tiver email activo."""
    from .models import Notification, NotificationPreference

    try:
        notif = Notification.objects.select_related(
            'recipient', 'actor'
        ).get(id=notification_id)
    except Notification.DoesNotExist:
        return

    prefs, _ = NotificationPreference.objects.get_or_create(user=notif.recipient)
    if prefs.channel not in ('email',) or not notif.recipient.security.email_verified:
        return

    try:
        send_mail(
            subject    = f'KwanzaConnect — {notif.title}',
            message    = notif.body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [notif.recipient.email],
            fail_silently  = False,
        )
        notif.is_sent_email = True
        notif.save(update_fields=['is_sent_email'])
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, notification_id: str):
    """
    Envia push notification para os dispositivos registados.
    Implementar com firebase-admin quando o FCM estiver configurado.
    """
    from .models import Notification, PushDevice

    try:
        notif = Notification.objects.select_related('recipient').get(id=notification_id)
    except Notification.DoesNotExist:
        return

    devices = PushDevice.objects.filter(
        user=notif.recipient, is_active=True
    )
    if not devices.exists():
        return

    # TODO: integrar firebase-admin
    # import firebase_admin
    # from firebase_admin import messaging
    # for device in devices:
    #     message = messaging.Message(
    #         notification=messaging.Notification(title=notif.title, body=notif.body),
    #         token=device.token,
    #     )
    #     messaging.send(message)

    notif.is_sent_push = True
    notif.save(update_fields=['is_sent_push'])