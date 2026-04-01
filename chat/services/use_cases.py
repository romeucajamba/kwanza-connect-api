"""
Use cases do módulo chat.
"""
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.db.models import Q
from ..models import Room, Message, RoomMember


class GetUserRoomsUseCase:
    """Lista as salas que o utilizador pertence."""
    def execute(self, user):
        return Room.objects.filter(
            members__user=user
        ).select_related('offer', 'offer__give_currency', 'offer__want_currency')\
         .prefetch_related('members__user')\
         .order_by('-created_at')


class GetRoomMessagesUseCase:
    """Obtém mensagens de uma sala com paginação."""
    def execute(self, user, room_id: str, limit: int = 50, offset: int = 0):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound('Sala não encontrada.')

        # Valida se o utilizador é membro
        if not room.members.filter(user=user).exists():
            raise PermissionDenied('Não tem permissão para aceder a esta conversa.')

        messages = Message.objects.filter(room=room).select_related('sender').order_by('-created_at')[offset:offset+limit]
        return reversed(list(messages))


class SendMessageUseCase:
    """Envia uma mensagem para uma sala."""
    def execute(self, user, room_id: str, data: dict) -> Message:
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound('Sala não encontrada.')

        # Valida se o utilizador é membro
        if not room.members.filter(user=user).exists():
            raise PermissionDenied('Não tem permissão para enviar mensagens para esta porta.')

        if room.status != 'active':
            raise ValidationError('Esta conversa está encerrada.')

        message = Message.objects.create(
            room=room,
            sender=user,
            content=data.get('content', ''),
            msg_type=data.get('msg_type', 'text'),
            file=data.get('file'),
            reply_to=data.get('reply_to'),
        )
        return message


class DeleteMessageUseCase:
    """Apaga logicamente uma mensagem."""
    def execute(self, user, message_id: str) -> None:
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise NotFound('Mensagem não encontrada.')

        if message.sender != user:
            raise PermissionDenied('Apenas o remetente pode apagar a mensagem.')

        message.soft_delete()
