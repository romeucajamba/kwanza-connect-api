import pytest
import uuid
from unittest.mock import Mock
from decimal import Decimal
from offers.services.use_cases import CreateOfferUseCase
from offers.domain.entities import OfferEntity, CurrencyEntity
from offers.domain.interfaces import IOfferRepository

def test_create_offer_success():
    # Arrange
    mock_repo = Mock(spec=IOfferRepository)
    
    aoa = CurrencyEntity(id=uuid.uuid4(), code="AOA", name="Kwanza", symbol="Kz")
    usd = CurrencyEntity(id=uuid.uuid4(), code="USD", name="Dollar", symbol="$")
    
    mock_repo.get_currency_by_code.side_effect = lambda code: aoa if code == "AOA" else usd
    mock_repo.get_exchange_rate.return_value = Mock(rate=Decimal("1000.0"))
    
    def side_effect_save(offer):
        return offer
    mock_repo.save_offer.side_effect = side_effect_save
    
    use_case = CreateOfferUseCase(repository=mock_repo)
    user_id = uuid.uuid4()
    data = {
        'give_currency_code': 'AOA',
        'want_currency_code': 'USD',
        'give_amount': 10000,
        'want_amount': 10,
        'offer_type': 'sell',
    }
    
    # Act
    offer = use_case.execute(user_id=user_id, data=data)
    
    # Assert
    assert offer.owner_id == user_id
    assert offer.give_currency_id == aoa.id
    assert offer.give_amount == Decimal("10000")
    mock_repo.save_offer.assert_called_once()
