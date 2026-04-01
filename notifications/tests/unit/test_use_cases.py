import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock
from notifications.services.use_cases import MarkNotificationReadUseCase
from notifications.domain.entities import NotificationEntity
from notifications.domain.interfaces import INotificationRepository

def test_mark_notification_read_success():
    # Arrange
    mock_repo = Mock(spec=INotificationRepository)
    notif_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    notif = NotificationEntity(
        id=notif_id, 
        recipient_id=user_id, 
        type='system', 
        title='Test', 
        body='Body',
        is_read=False
    )
    
    mock_repo.get_notification_by_id.return_value = notif
    
    use_case = MarkNotificationReadUseCase(repository=mock_repo)
    
    # Act
    use_case.execute(user_id=user_id, notification_id=notif_id)
    
    # Assert
    assert notif.is_read is True
    assert notif.read_at is not None
    mock_repo.save_notification.assert_called_once_with(notif)

def test_mark_all_notifications_read():
    # Arrange
    mock_repo = Mock(spec=INotificationRepository)
    user_id = uuid.uuid4()
    
    use_case = MarkNotificationReadUseCase(repository=mock_repo)
    
    # Act
    use_case.execute(user_id=user_id, notification_id=None)
    
    # Assert
    mock_repo.mark_all_as_read.assert_called_once_with(user_id)
