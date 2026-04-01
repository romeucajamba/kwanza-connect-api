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
    UpdateNotificationPreferencesUseCase
)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        limit  = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        qs     = GetUserNotificationsUseCase().execute(user=request.user, limit=limit, offset=offset)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def post(self, request, notification_id: str = None):
        """Marca uma ou todas as notificações como lidas."""
        MarkNotificationReadUseCase().execute(user=request.user, notification_id=notification_id)
        return success_response(message='Notificações marcadas como lidas.')


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        from ..models import NotificationPreference
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(prefs)
        return success_response(data=serializer.data)

    @extend_schema(request=NotificationPreferenceSerializer, tags=['Notificações'])
    def patch(self, request):
        serializer = NotificationPreferenceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        prefs = UpdateNotificationPreferencesUseCase().execute(user=request.user, data=serializer.validated_data)
        return success_response(
            data=NotificationPreferenceSerializer(prefs).data,
            message='Preferências actualizadas com sucesso.'
        )


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Notificações'])
    def get(self, request):
        from ..models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return success_response(data={'unread_count': count})
