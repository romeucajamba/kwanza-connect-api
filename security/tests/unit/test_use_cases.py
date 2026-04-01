import pytest
from unittest.mock import Mock
from datetime import datetime
from security.services.use_cases import VerifyAPIKeyUseCase
from security.domain.entities import APIKeyEntity
from security.domain.interfaces import ISecurityRepository
import hashlib

def test_verify_api_key_success():
    # Arrange
    mock_repo = Mock(spec=ISecurityRepository)
    prefix = "abcd1234"
    raw_key = f"kc_{prefix}.mysecret"
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    
    entity = APIKeyEntity(
        id=1,
        name="Test App",
        prefix=prefix,
        hashed_key=hashed,
        is_active=True
    )
    
    mock_repo.get_api_key_by_prefix.return_value = entity
    
    use_case = VerifyAPIKeyUseCase(repository=mock_repo)
    
    # Act
    is_valid = use_case.execute(raw_key)
    
    # Assert
    assert is_valid is True
    assert entity.last_used is not None
    mock_repo.save_api_key.assert_called_once_with(entity)

def test_verify_api_key_invalid():
    # Arrange
    mock_repo = Mock(spec=ISecurityRepository)
    mock_repo.get_api_key_by_prefix.return_value = None
    
    use_case = VerifyAPIKeyUseCase(repository=mock_repo)
    
    # Act
    is_valid = use_case.execute("kc_nonexistent.secret")
    
    # Assert
    assert is_valid is False
