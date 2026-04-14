"""
Controllers do módulo chat.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app.exceptions import success_response, created_response
from app.pagination import StandardPagination
from ..infra.serializers import RoomSerializer, MessageSerializer, MessageCreateSerializer
from ..services.use_cases import (
    GetUserRoomsUseCase, GetRoomMessagesUseCase, 
    SendMessageUseCase, DeleteMessageUseCase
)
from ..infra.repositories import DjangoChatRepository
from app.services.websocket_service import ChannelsWebSocketService
from app.services.cloudinary_storage import CloudinaryStorageService
import uuid
from rest_framework.exceptions import NotFound


class RoomListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def get(self, request):
        repo = DjangoChatRepository()
        qs         = GetUserRoomsUseCase(repo).execute(user_id=request.user.id)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = RoomSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def get(self, request, room_id: str):
        repo = DjangoChatRepository()
        room = repo.get_room_by_id(uuid.UUID(room_id))
        if not room:
            raise NotFound('Sala não encontrada.')
        
        # Valida se o utilizador é membro
        member = repo.get_member_by_room_and_user(uuid.UUID(room_id), request.user.id)
        if not member:
            raise NotFound('Sala não encontrada ou não pertence ao utilizador.')

        serializer = RoomSerializer(room, context={'request': request})
        return success_response(data=serializer.data)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Mensagens'],
        parameters=[
            OpenApiParameter('limit', int, required=False),
            OpenApiParameter('before', str, required=False),
        ]
    )
    def get(self, request, room_id: str):
        repo = DjangoChatRepository()
        limit  = int(request.query_params.get('limit', 50))
        before = request.query_params.get('before')
        before_id = uuid.UUID(before) if before else None
        
        messages   = GetRoomMessagesUseCase(repo).execute(
            user_id=request.user.id, 
            room_id=uuid.UUID(room_id), 
            limit=limit, 
            before=before_id
        )
        serializer = MessageSerializer(messages, many=True)
        return success_response(data=serializer.data)

    @extend_schema(request=MessageCreateSerializer, tags=['Mensagens'])
    def post(self, request, room_id: str):
        repo = DjangoChatRepository()
        ws_service = ChannelsWebSocketService()
        storage_service = CloudinaryStorageService()
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = SendMessageUseCase(repo, ws_service, storage_service).execute(
            user_id=request.user.id, 
            room_id=uuid.UUID(room_id), 
            data=serializer.validated_data
        )
        return created_response(
            data=MessageSerializer(message).data,
            message='Mensagem enviada com sucesso.'
        )


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def delete(self, request, message_id: str):
        repo = DjangoChatRepository()
        DeleteMessageUseCase(repo).execute(
            user_id=request.user.id, 
            message_id=uuid.UUID(message_id)
        )
        return success_response(message='Mensagem apagada com sucesso.')
