import pytest
import uuid
from unittest.mock import Mock
from chat.services.use_cases import SendMessageUseCase
from chat.domain.entities import RoomEntity, RoomMemberEntity, MessageEntity
from chat.domain.interfaces import IChatRepository

def test_send_message_success():
    # Arrange
    mock_repo = Mock(spec=IChatRepository)
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    room = RoomEntity(id=room_id, status='active')
    member = RoomMemberEntity(id=uuid.uuid4(), room_id=room_id, user_id=user_id)
    
    mock_repo.get_room_by_id.return_value = room
    mock_repo.get_member_by_room_and_user.return_value = member
    
    def side_effect_save(message):
        return message
    mock_repo.save_message.side_effect = side_effect_save
    
    use_case = SendMessageUseCase(repository=mock_repo)
    data = {'content': 'Hello world', 'msg_type': 'text'}
    
    # Act
    message = use_case.execute(user_id=user_id, room_id=room_id, data=data)
    
    # Assert
    assert message.sender_id == user_id
    assert message.room_id == room_id
    assert message.content == 'Hello world'
    mock_repo.save_message.assert_called_once()

def test_send_message_not_member():
    # Arrange
    mock_repo = Mock(spec=IChatRepository)
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    room = RoomEntity(id=room_id, status='active')
    mock_repo.get_room_by_id.return_value = room
    mock_repo.get_member_by_room_and_user.return_value = None
    
    use_case = SendMessageUseCase(repository=mock_repo)
    
    # Act & Assert
    from rest_framework.exceptions import PermissionDenied
    with pytest.raises(PermissionDenied):
        use_case.execute(user_id=user_id, room_id=room_id, data={'content': 'hi'})
