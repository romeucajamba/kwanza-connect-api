import pytest
from unittest.mock import Mock
from decimal import Decimal
from rates.services.use_cases import ConvertAmountUseCase
from rates.domain.interfaces import IRatesRepository

def test_convert_amount_success():
    # Arrange
    mock_repo = Mock(spec=IRatesRepository)
    mock_repo.get_exchange_rate.return_value = Decimal("1000.0")
    
    use_case = ConvertAmountUseCase(repository=mock_repo)
    
    # Act
    result = use_case.execute(from_code="USD", to_code="AOA", amount=Decimal("10"))
    
    # Assert
    assert result['converted_amount'] == Decimal("10000.0")
    assert result['rate'] == Decimal("1000.0")
    mock_repo.get_exchange_rate.assert_called_once_with("USD", "AOA")

def test_convert_amount_not_found():
    # Arrange
    mock_repo = Mock(spec=IRatesRepository)
    mock_repo.get_exchange_rate.return_value = None
    
    use_case = ConvertAmountUseCase(repository=mock_repo)
    
    # Act & Assert
    from rest_framework.exceptions import NotFound
    with pytest.raises(NotFound):
        use_case.execute(from_code="USD", to_code="XYZ", amount=Decimal("10"))
