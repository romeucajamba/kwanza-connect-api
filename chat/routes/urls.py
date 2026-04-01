from django.urls import path
from ..controllers.views import RoomListView, RoomDetailView, MessageListView, MessageDetailView

urlpatterns = [
    # Salas de conversa
    path('rooms/',                   RoomListView.as_view(),       name='room-list'),
    path('rooms/<str:room_id>/',     RoomDetailView.as_view(),     name='room-detail'),

    # Mensagens em uma sala
    path('rooms/<str:room_id>/messages/', MessageListView.as_view(),    name='message-list'),

    # Gestão de mensagens individuais
    path('messages/<str:message_id>/',    MessageDetailView.as_view(),  name='message-detail'),
]
