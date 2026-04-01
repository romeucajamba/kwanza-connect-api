from django.urls import path
from ..controllers.views import (
    NotificationListView, NotificationMarkReadView, 
    NotificationPreferenceView, UnreadCountView
)

urlpatterns = [
    # Notificações
    path('',                        NotificationListView.as_view(),       name='notification-list'),
    path('unread-count/',           UnreadCountView.as_view(),            name='notification-unread-count'),
    path('mark-read/',              NotificationMarkReadView.as_view(),    name='notification-mark-all-read'),
    path('mark-read/<str:notification_id>/', NotificationMarkReadView.as_view(), name='notification-mark-one-read'),

    # Preferências
    path('preferences/',             NotificationPreferenceView.as_view(), name='notification-preferences'),
]
