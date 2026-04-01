import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from ...models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Canal pessoal de notificações.
    Cada utilizador liga-se a: ws/notifications/
    e é colocado no grupo: notifications_{user_id}
    """

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Envia badge com total não lido ao conectar
        unread = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'event':        'connected',
            'unread_count': unread,
        }))

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = data.get('action')

        if action == 'mark_read':
            notification_id = data.get('notification_id')
            if notification_id:
                await self.mark_one_read(notification_id)
            else:
                await self.mark_all_read()

            unread = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'event':        'read_updated',
                'unread_count': unread,
            }))

    # ── handler chamado pelo NotificationService/Celery ──

    async def push_notification(self, event):
        """Recebe do group_send e reencaminha para o WebSocket do cliente."""
        await self.send(text_data=json.dumps({
            'event':        'new_notification',
            'notification': event['notification'],
        }))

        # Actualiza badge em tempo real
        unread = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'event':        'badge_update',
            'unread_count': unread,
        }))

    # ── helpers de base de dados (async safe) ──

    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(
            recipient=self.user, is_read=False
        ).count()

    @database_sync_to_async
    def mark_one_read(self, notification_id):
        Notification.objects.filter(
            id=notification_id, recipient=self.user
        ).update(is_read=True, read_at=timezone.now())

    @database_sync_to_async
    def mark_all_read(self):
        Notification.objects.filter(
            recipient=self.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())