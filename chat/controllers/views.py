"""
Controllers do módulo chat.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app.exceptions import success_response, created_response
from app.pagination import StandardPagination
from ..infra.serializers import RoomSerializer, MessageSerializer, MessageCreateSerializer
from ..services.use_cases import GetUserRoomsUseCase, GetRoomMessagesUseCase, SendMessageUseCase, DeleteMessageUseCase


class RoomListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def get(self, request):
        qs         = GetUserRoomsUseCase().execute(user=request.user)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = RoomSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def get(self, request, room_id: str):
        try:
            from ..models import Room
            room = Room.objects.get(id=room_id, members__user=request.user)
        except Room.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Sala não encontrada ou não pertence ao utilizador.')
        serializer = RoomSerializer(room, context={'request': request})
        return success_response(data=serializer.data)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Mensagens'],
        parameters=[
            OpenApiParameter('limit', int, required=False),
            OpenApiParameter('offset', int, required=False),
        ]
    )
    def get(self, request, room_id: str):
        limit  = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        messages   = GetRoomMessagesUseCase().execute(user=request.user, room_id=room_id, limit=limit, offset=offset)
        serializer = MessageSerializer(messages, many=True)
        return success_response(data=serializer.data)

    @extend_schema(request=MessageCreateSerializer, tags=['Mensagens'])
    def post(self, request, room_id: str):
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = SendMessageUseCase().execute(user=request.user, room_id=room_id, data=serializer.validated_data)
        return created_response(
            data=MessageSerializer(message).data,
            message='Mensagem enviada com sucesso.'
        )


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Mensagens'])
    def delete(self, request, message_id: str):
        DeleteMessageUseCase().execute(user=request.user, message_id=message_id)
        return success_response(message='Mensagem apagada com sucesso.')
