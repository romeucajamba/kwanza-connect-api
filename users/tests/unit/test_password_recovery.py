import pytest
import uuid
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from users.services.use_cases import ForgotPasswordUseCase, ResetPasswordUseCase
from users.domain.entities import UserEntity, UserSecurityEntity
from users.domain.interfaces import IUserRepository
from users.infra.email_service import IEmailService

def test_forgot_password_success():
    # Arrange
    mock_repo = Mock(spec=IUserRepository)
    mock_email = Mock(spec=IEmailService)
    
    user_id = uuid.uuid4()
    user = UserEntity(id=user_id, email="test@example.com", full_name="Test User")
    security = UserSecurityEntity(id=uuid.uuid4(), user_id=user_id)
    
    mock_repo.get_by_email.return_value = user
    mock_repo.get_security_by_user_id.return_value = security
    
    use_case = ForgotPasswordUseCase(mock_repo, mock_email)
    
    # Act
    use_case.execute("test@example.com")
    
    # Assert
    assert security.password_reset_token != ""
    assert security.password_reset_expires is not None
    mock_repo.update_security.assert_called_once_with(security)
    mock_email.send_email.assert_called_once()

def test_reset_password_success():
    # Arrange
    mock_repo = Mock(spec=IUserRepository)
    security_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Simula token hashed
    token = "raw_token"
    import hashlib
    hashed = hashlib.sha256(token.encode()).hexdigest()
    
    security = UserSecurityEntity(
        id=security_id, 
        user_id=user_id,
        password_reset_token=hashed,
        password_reset_expires=datetime.now() + timedelta(hours=1)
    )
    
    mock_repo.get_security_by_reset_token.return_value = security
    
    use_case = ResetPasswordUseCase(mock_repo)
    
    # Act
    with patch('users.models.User.objects.get') as mock_get:
        mock_django_user = Mock()
        mock_get.return_value = mock_django_user
        
        use_case.execute(token, "new_password_123")
        
        # Assert
        mock_django_user.set_password.assert_called_once_with("new_password_123")
        assert security.password_reset_token == ""
        mock_repo.update_security.assert_called_once_with(security)
