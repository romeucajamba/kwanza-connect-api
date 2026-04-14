"""
Controllers do módulo de notificações.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app.exceptions import success_response
from app.pagination import StandardPagination
from ..infra.serializers import NotificationSerializer, NotificationPreferenceSerializer
from ..services.use_cases import (
    GetUserNotificationsUseCase, MarkNotificationReadUseCase, 
    UpdateNotificationPreferencesUseCase, GetNotificationPreferencesUseCase
)
from ..infra.repositories import DjangoNotificationRepository
from app.services.websocket_service import ChannelsWebSocketService
import uuid


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        repo = DjangoNotificationRepository()
        limit  = int(request.query_params.get('limit', 20))
        only_unread = request.query_params.get('unread') == 'true'
        
        qs     = GetUserNotificationsUseCase(repo).execute(
            user_id=request.user.id, 
            limit=limit, 
            only_unread=only_unread
        )
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def post(self, request, notification_id: str = None):
        """Marca uma ou todas as notificações como lidas."""
        repo = DjangoNotificationRepository()
        ws_service = ChannelsWebSocketService()
        notif_id = uuid.UUID(notification_id) if notification_id else None
        MarkNotificationReadUseCase(repo, ws_service).execute(
            user_id=request.user.id, 
            notification_id=notif_id
        )
        return success_response(message='Notificações marcadas como lidas.')


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        repo = DjangoNotificationRepository()
        prefs = GetNotificationPreferencesUseCase(repo).execute(user_id=request.user.id)
        serializer = NotificationPreferenceSerializer(prefs)
        return success_response(data=serializer.data)

    @extend_schema(request=NotificationPreferenceSerializer, tags=['Notificações'])
    def patch(self, request):
        repo = DjangoNotificationRepository()
        serializer = NotificationPreferenceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        prefs = UpdateNotificationPreferencesUseCase(repo).execute(
            user_id=request.user.id, 
            data=serializer.validated_data
        )
        return success_response(
            data=NotificationPreferenceSerializer(prefs).data,
            message='Preferências actualizadas com sucesso.'
        )


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        repo = DjangoNotificationRepository()
        notifs = repo.list_user_notifications(user_id=request.user.id, only_unread=True)
        return success_response(data={'unread_count': len(notifs)})
