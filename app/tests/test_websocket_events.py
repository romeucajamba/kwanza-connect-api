import pytest
import uuid
from unittest.mock import Mock, patch
from chat.services.use_cases import SendMessageUseCase
from chat.domain.interfaces import IChatRepository
from app.services.websocket_service import ChannelsWebSocketService
from notifications.services.use_cases import MarkNotificationReadUseCase
from notifications.domain.interfaces import INotificationRepository

@pytest.fixture
def mock_channel_layer():
    with patch('app.services.websocket_service.get_channel_layer') as mock:
        layer = Mock()
        mock.return_value = layer
        yield layer

def test_send_message_triggers_websocket(mock_channel_layer):
    # Arrange
    mock_repo = Mock(spec=IChatRepository)
    ws_service = ChannelsWebSocketService()
    use_case = SendMessageUseCase(mock_repo, ws_service)
    
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    mock_room = Mock()
    mock_room.is_active.return_value = True
    mock_repo.get_room_by_id.return_value = mock_room
    mock_repo.get_member_by_room_and_user.return_value = Mock()
    
    saved_msg = Mock()
    saved_msg.id = uuid.uuid4()
    saved_msg.content = "Olá"
    saved_msg.msg_type = "text"
    saved_msg.created_at = None
    mock_repo.save_message.return_value = saved_msg
    
    # Act
    use_case.execute(user_id, room_id, {"content": "Olá"})
    
    # Assert
    mock_channel_layer.group_send.assert_called_once()
    args, kwargs = mock_channel_layer.group_send.call_args
    assert args[0] == f"chat_{room_id}"
    assert args[1]["event"] == "new_message"

def test_mark_notifications_read_triggers_websocket(mock_channel_layer):
    # Arrange
    mock_repo = Mock(spec=INotificationRepository)
    ws_service = ChannelsWebSocketService()
    use_case = MarkNotificationReadUseCase(mock_repo, ws_service)
    
    user_id = uuid.uuid4()
    mock_repo.get_unread_count.return_value = 5
    
    # Act
    use_case.execute(user_id, notification_id=None) # Mark all read
    
    # Assert
    mock_channel_layer.group_send.assert_called_once()
    args, kwargs = mock_channel_layer.group_send.call_args
    assert args[0] == f"user_{user_id}"
    assert args[1]["event"] == "unread_count_update"
    assert args[1]["data"]["unread_count"] == 5
