import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, RoomMember, MessageRead


class ChatConsumer(AsyncWebsocketConsumer):

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

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        await self.mark_room_read()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        action  = data.get('action')

        if action == 'send_message':
            message = await self.save_message(data)
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':       'chat_message',
                    'message_id': str(message.id),
                    'content':    message.content,
                    'msg_type':   message.msg_type,
                    'sender_id':  str(self.user.id),
                    'sender_name': self.user.full_name,
                    'reply_to':   data.get('reply_to'),
                    'created_at': message.created_at.isoformat(),
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
                    'type':    'messages_read',
                    'user_id': str(self.user.id),
                }
            )

    # ── handlers de eventos do grupo ──

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({**event, 'event': 'message'}))

    async def user_typing(self, event):
        if str(self.user.id) != event['user_id']:
            await self.send(text_data=json.dumps({**event, 'event': 'typing'}))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({**event, 'event': 'read'}))

    # ── helpers de base de dados ──

    @database_sync_to_async
    def check_membership(self):
        return RoomMember.objects.filter(
            room_id=self.room_id, user=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, data):
        return Message.objects.create(
            room_id   = self.room_id,
            sender    = self.user,
            msg_type  = data.get('msg_type', 'text'),
            content   = data.get('content', ''),
            reply_to_id = data.get('reply_to'),
        )

    @database_sync_to_async
    def mark_room_read(self):
        RoomMember.objects.filter(
            room_id=self.room_id, user=self.user
        ).update(last_read_at=__import__('django.utils.timezone', fromlist=['timezone']).timezone.now())