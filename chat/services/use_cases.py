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
from app.services.websocket_service import IWebSocketService
from app.services.storage import IStorageService

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
    def __init__(self, repository: IChatRepository, ws_service: IWebSocketService = None, storage_service: IStorageService = None):
        self.repository = repository
        self.ws_service = ws_service
        self.storage_service = storage_service

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

        file_url = data.get('file')
        file_name = data.get('file_name', '')
        file_size = data.get('file_size')

        # Upload de ficheiro se fornecido como buffer/arquivo
        if file_url and self.storage_service and not isinstance(file_url, str):
            orig_name = getattr(file_url, 'name', 'file')
            file_url = self.storage_service.upload(
                file_url.read() if hasattr(file_url, 'read') else file_url,
                f"chat-{room_id}-{uuid.uuid4().hex[:8]}",
                folder=f"chat/{room_id}"
            )
            file_name = orig_name
            # Se for imagem, forçamos o tipo se não estiver definido
            if not data.get('msg_type') or data.get('msg_type') == 'text':
                data['msg_type'] = 'image' if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'file'

        message = MessageEntity(
            id=uuid.uuid4(),
            room_id=room_id,
            sender_id=user_id,
            content=data.get('content', ''),
            msg_type=data.get('msg_type', 'text'),
            file=file_url,
            file_name=file_name,
            file_size=file_size,
            reply_to_id=data.get('reply_to_id'),
        )
        saved_msg = self.repository.save_message(message)
        
        # Notificação em Tempo Real
        if self.ws_service:
            self.ws_service.send_to_room(
                room_id=str(room_id),
                event_type="new_message",
                payload={
                    "id": str(saved_msg.id),
                    "sender_id": str(user_id),
                    "content": saved_msg.content,
                    "msg_type": saved_msg.msg_type,
                    "created_at": saved_msg.created_at.isoformat() if saved_msg.created_at else None
                }
            )
            
        return saved_msg

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
    def __init__(self, repository: IChatRepository, ws_service: IWebSocketService = None):
        self.repository = repository
        self.ws_service = ws_service

    def execute(self, user_id: uuid.UUID, room_id: uuid.UUID) -> None:
        member = self.repository.get_member_by_room_and_user(room_id, user_id)
        if not member:
            raise NotFound('Membro não encontrado.')
        
        member.last_read_at = datetime.now()
        self.repository.save_member(member)
        
        if self.ws_service:
            self.ws_service.send_to_user(
                user_id=str(user_id),
                event_type="room_read",
                payload={"room_id": str(room_id)}
            )
