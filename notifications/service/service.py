from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Notification, NotificationPreference, NotificationType
from .tasks  import send_notification_email, send_push_notification


class NotificationService:
    """
    Ponto único de criação e entrega de notificações.

    Uso:
        NotificationService.send(
            recipient = user,
            actor     = outro_user,
            type      = NotificationType.NEW_INTEREST,
            payload   = {'offer_id': '...', 'redirect': '/offers/123'},
        )
    """

    # Textos centralizados por tipo
    TEMPLATES = {
        NotificationType.NEW_INTEREST: {
            'title': 'Novo interesse na tua oferta',
            'body':  '{actor} está interessado na tua oferta de {give_amount} {give_currency}.',
        },
        NotificationType.INTEREST_ACCEPTED: {
            'title': 'O teu interesse foi aceite!',
            'body':  '{actor} aceitou o teu interesse. Podes agora negociar no chat.',
        },
        NotificationType.INTEREST_REJECTED: {
            'title': 'Interesse não aceite',
            'body':  '{actor} não aceitou o teu interesse nesta oferta.',
        },
        NotificationType.INTEREST_CANCELLED: {
            'title': 'Interesse cancelado',
            'body':  '{actor} cancelou o interesse na tua oferta.',
        },
        NotificationType.OFFER_EXPIRED: {
            'title': 'A tua oferta expirou',
            'body':  'A tua oferta de {give_amount} {give_currency} foi encerrada automaticamente.',
        },
        NotificationType.NEW_MESSAGE: {
            'title': 'Nova mensagem de {actor}',
            'body':  '{actor}: {preview}',
        },
        NotificationType.DEAL_ACCEPTED: {
            'title': 'Acordo aceite',
            'body':  '{actor} aceitou o acordo. Combinem os detalhes fora da plataforma.',
        },
        NotificationType.DEAL_CANCELLED: {
            'title': 'Acordo cancelado',
            'body':  '{actor} cancelou o acordo.',
        },
        NotificationType.ACCOUNT_VERIFIED: {
            'title': 'Conta verificada',
            'body':  'Os teus documentos foram aprovados. A tua conta está agora verificada.',
        },
        NotificationType.ACCOUNT_REJECTED: {
            'title': 'Verificação rejeitada',
            'body':  'Os teus documentos foram rejeitados. Verifica o motivo no teu perfil.',
        },
        NotificationType.RATE_ALERT: {
            'title': 'Alerta de câmbio: {from_currency}/{to_currency}',
            'body':  'A taxa atingiu {rate}. O teu alerta foi activado.',
        },
        NotificationType.SYSTEM: {
            'title': 'Aviso do sistema',
            'body':  '{message}',
        },
    }

    @classmethod
    def send(
        cls,
        recipient,
        notification_type: str,
        payload: dict = None,
        actor=None,
    ) -> Notification | None:
        """
        Cria a notificação e entrega-a por todos os canais activos.
        Devolve o objecto Notification ou None se o utilizador
        tiver o tipo desactivado nas preferências.
        """
        payload = payload or {}

        # Verifica preferências do utilizador
        prefs, _ = NotificationPreference.objects.get_or_create(user=recipient)
        pref_key = notification_type.replace('-', '_')
        if not prefs.allows(pref_key):
            return None

        # Constrói título e corpo usando o template
        template = cls.TEMPLATES.get(notification_type, {
            'title': 'Notificação',
            'body':  '',
        })

        fmt_ctx = {
            'actor': actor.full_name if actor else 'Sistema',
            **payload,
        }
        title = cls._fmt(template['title'], fmt_ctx)
        body  = cls._fmt(template['body'],  fmt_ctx)

        # Persiste na base de dados
        notification = Notification.objects.create(
            recipient = recipient,
            actor     = actor,
            type      = notification_type,
            title     = title,
            body      = body,
            payload   = payload,
        )

        # Entrega em tempo real via WebSocket
        cls._send_websocket(notification)

        # Email e push via Celery (assíncrono, não bloqueia)
        send_notification_email.delay(str(notification.id))
        send_push_notification.delay(str(notification.id))

        return notification

    # ── helpers ──────────────────────────────

    @staticmethod
    def _fmt(template: str, ctx: dict) -> str:
        try:
            return template.format(**ctx)
        except KeyError:
            return template

    @staticmethod
    def _send_websocket(notification: Notification):
        """
        Envia a notificação para o canal WebSocket do utilizador.
        Cada utilizador autenticado tem um grupo próprio:
        'notifications_{user_id}'
        """
        channel_layer = get_channel_layer()
        group_name    = f'notifications_{notification.recipient_id}'

        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type':         'push_notification',
                    'notification': notification.to_websocket_payload(),
                }
            )
            notification.is_sent_ws = True
            notification.save(update_fields=['is_sent_ws'])
        except Exception:
            pass  # falha silenciosa — o utilizador verá ao abrir a app

    @classmethod
    def mark_all_read(cls, user):
        Notification.objects.filter(
            recipient=user, is_read=False
        ).update(is_read=True, read_at=timezone.now())

    @classmethod
    def unread_count(cls, user) -> int:
        return Notification.objects.filter(
            recipient=user, is_read=False
        ).count()