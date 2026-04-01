import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Inicializa o Django primeiro, antes de qualquer import dos apps
django_asgi_app = get_asgi_application()

# Imports após a inicialização do Django
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns as chat_ws
from notifications.routing import websocket_urlpatterns as notifications_ws

application = ProtocolTypeRouter({
    # HTTP → gestão normal do Django
    'http': django_asgi_app,

    # WebSocket → JWT via AuthMiddlewareStack
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat_ws + notifications_ws
            )
        )
    ),
})
