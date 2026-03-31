"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
#import apps.chat.routing
#import apps.notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_wsgi_application()

"""application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.chat.routing.websocket_urlpatterns +
            apps.notifications.routing.websocket_urlpatterns
        )
    ),
})"""
