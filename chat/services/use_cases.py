"""
Use cases do módulo chat.
Orquestra repositórios e lógica de negócio operando sobre Entidades.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from ..domain.entities import RoomEntity, RoomMemberEntity, MessageEntity
from ..domain.interfaces import IChatRepository

class GetUserRoomsUseCase:
    def __init__(self, repository: IChatRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID) -> List[RoomEntity]:
        return self.repository.list_user_rooms(user_id)

class GetRoomMessagesUseCase:
    def __init__(self, repository: IChatRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, room_id: uuid.UUID, limit: int = 50, before: Optional[uuid.UUID] = None) -> List[MessageEntity]:
        # Valida se o utilizador é membro
        member = self.repository.get_member_by_room_and_user(room_id, user_id)
        if not member:
            raise PermissionDenied('Não tem permissão para aceder a esta conversa.')

        return self.repository.list_room_messages(room_id, limit, before)

class SendMessageUseCase:
    def __init__(self, repository: IChatRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, room_id: uuid.UUID, data: dict) -> MessageEntity:
        room = self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFound('Sala não encontrada.')

        # Valida se o utilizador é membro
        member = self.repository.get_member_by_room_and_user(room_id, user_id)
        if not member:
            raise PermissionDenied('Não tem permissão para enviar mensagens nesta sala.')

        if not room.is_active():
            raise ValidationError('Esta conversa está encerrada.')

        message = MessageEntity(
            id=uuid.uuid4(),
            room_id=room_id,
            sender_id=user_id,
            content=data.get('content', ''),
            msg_type=data.get('msg_type', 'text'),
            reply_to_id=data.get('reply_to_id'),
        )
        return self.repository.save_message(message)

class DeleteMessageUseCase:
    def __init__(self, repository: IChatRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, message_id: uuid.UUID) -> None:
        message = self.repository.get_message_by_id(message_id)
        if not message:
            raise NotFound('Mensagem não encontrada.')

        if message.sender_id != user_id:
            raise PermissionDenied('Apenas o remetente pode apagar a mensagem.')

        message.is_deleted = True
        message.content = ""
        # message.file = None (handled in repo update)
        self.repository.save_message(message)

class MarkRoomAsReadUseCase:
    def __init__(self, repository: IChatRepository):
        self.repository = repository

    def execute(self, user_id: uuid.UUID, room_id: uuid.UUID) -> None:
        member = self.repository.get_member_by_room_and_user(room_id, user_id)
        if not member:
            raise NotFound('Membro não encontrado.')
        
        member.last_read_at = datetime.now()
        self.repository.save_member(member)
