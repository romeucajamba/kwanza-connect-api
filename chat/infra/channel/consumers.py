import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from ...models import Room, Message, RoomMember, MessageRead


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para salas de chat individuais.
    Identifica o utilizador pelo token e valida se pertence à sala.
    """

    async def connect(self):
        self.room_id   = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        self.user       = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        is_member = await self.check_membership()
        if not is_member:
            await self.close()
            return

        # Adiciona ao grupo da sala
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Marca como lido ao entrar
        await self.mark_room_read()

    async def disconnect(self, code):
        if hasattr(self, 'room_group'):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        action = data.get('action')

        if action == 'send_message':
            message_data = await self.save_message(data)
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':     'chat_message',
                    'message':  message_data,
                }
            )

        elif action == 'typing':
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':      'user_typing',
                    'user_id':   str(self.user.id),
                    'user_name': self.user.full_name,
                    'is_typing': data.get('is_typing', False),
                }
            )

        elif action == 'mark_read':
            await self.mark_room_read()
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':     'messages_read',
                    'user_id':  str(self.user.id),
                }
            )

    # ── Handlers de eventos do grupo ──

    async def chat_message(self, event):
        """Envia nova mensagem para o WebSocket do cliente."""
        await self.send(text_data=json.dumps({
            'event':   'message',
            'message': event['message'],
        }))

    async def user_typing(self, event):
        """Notifica outros utilizadores que alguém está a escrever."""
        if str(self.user.id) != event['user_id']:
            await self.send(text_data=json.dumps({
                'event':     'typing',
                'user_id':   event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing'],
            }))

    async def messages_read(self, event):
        """Notifica que as mensagens foram lidas."""
        if str(self.user.id) != event['user_id']:
            await self.send(text_data=json.dumps({
                'event':   'read',
                'user_id': event['user_id'],
            }))

    # ── Helpers de base de dados (async safe) ──

    @database_sync_to_async
    def check_membership(self):
        return RoomMember.objects.filter(
            room_id=self.room_id, user=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, data):
        msg = Message.objects.create(
            room_id     = self.room_id,
            sender      = self.user,
            msg_type    = data.get('msg_type', 'text'),
            content     = data.get('content', ''),
            reply_to_id = data.get('reply_to'),
        )
        # Serialização manual simples para o payload WS (evita problemas de circularidade)
        return {
            'id':          str(msg.id),
            'room_id':     str(msg.room_id),
            'sender_id':   str(msg.sender_id),
            'sender_name': msg.sender.full_name,
            'content':     msg.content,
            'msg_type':    msg.msg_type,
            'created_at':  msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def mark_room_read(self):
        RoomMember.objects.filter(
            room_id=self.room_id, user=self.user
        ).update(last_read_at=timezone.now())
