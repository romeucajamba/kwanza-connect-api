import logging
from abc import ABC, abstractmethod
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class IWebSocketService(ABC):
    @abstractmethod
    def send_to_user(self, user_id: str, event_type: str, payload: dict) -> None:
        """Envia um evento para um utilizador específico (todas as suas abas)."""
        pass

    @abstractmethod
    def send_to_room(self, room_id: str, event_type: str, payload: dict) -> None:
        """Envia um evento para todos os membros numa sala de chat."""
        pass

class ChannelsWebSocketService(IWebSocketService):
    def __init__(self):
        self.channel_layer = get_channel_layer()

    def send_to_user(self, user_id: str, event_type: str, payload: dict) -> None:
        if not self.channel_layer:
            logger.warning("Channel layer not configured. Skipping WebSocket send.")
            return

        group_name = f"user_{user_id}"
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                "type": "user_event",
                "event": event_type,
                "data": payload
            }
        )

    def send_to_room(self, room_id: str, event_type: str, payload: dict) -> None:
        if not self.channel_layer:
            logger.warning("Channel layer not configured. Skipping WebSocket send.")
            return

        group_name = f"chat_{room_id}"
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message",
                "event": event_type,
                "data": payload
            }
        )

# Mock para testes
class MockWebSocketService(IWebSocketService):
    def send_to_user(self, user_id: str, event_type: str, payload: dict) -> None:
        print(f"[WS-USER] User: {user_id}, Event: {event_type}, Payload: {payload}")

    def send_to_room(self, room_id: str, event_type: str, payload: dict) -> None:
        print(f"[WS-ROOM] Room: {room_id}, Event: {event_type}, Payload: {payload}")
