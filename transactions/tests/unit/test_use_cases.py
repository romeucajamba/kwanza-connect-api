import pytest
import uuid
from unittest.mock import Mock
from decimal import Decimal
from transactions.services.use_cases import ConfirmDealUseCase, IOfferService, IChatService, INotificationService
from transactions.domain.entities import TransactionEntity
from transactions.domain.interfaces import ITransactionRepository

@pytest.mark.django_db
def test_confirm_deal_success():
    # Arrange
    mock_repo = Mock(spec=ITransactionRepository)
    mock_offer_service = Mock(spec=IOfferService)
    mock_chat_service = Mock(spec=IChatService)
    mock_notif_service = Mock(spec=INotificationService)
    
    offer_id = uuid.uuid4()
    room_id = uuid.uuid4()
    user_id = uuid.uuid4()
    buyer_id = uuid.uuid4()
    give_cur_id = uuid.uuid4()
    want_cur_id = uuid.uuid4()
    
    mock_offer_service.get_offer_details.return_value = {
        'id': offer_id,
        'owner_id': user_id,
        'give_currency_id': give_cur_id,
        'give_amount': Decimal("100"),
        'want_currency_id': want_cur_id,
        'want_amount': Decimal("10"),
        'exchange_rate_snapshot': Decimal("0.1")
    }
    mock_chat_service.get_other_participant.return_value = buyer_id
    
    def side_effect_save(tx):
        return tx
    mock_repo.save_transaction.side_effect = side_effect_save
    
    use_case = ConfirmDealUseCase(
        repository=mock_repo,
        offer_service=mock_offer_service,
        chat_service=mock_chat_service,
        notification_service=mock_notif_service
    )
    
    # Act
    tx = use_case.execute(user_id=user_id, offer_id=offer_id, room_id=room_id)
    
    # Assert
    assert tx.seller_id == user_id
    assert tx.buyer_id == buyer_id
    assert tx.status == 'completed'
    mock_repo.save_transaction.assert_called_once()
    mock_offer_service.close_offer.assert_called_once_with(offer_id)
    mock_chat_service.close_room.assert_called_once_with(room_id)
    mock_notif_service.notify_transaction_completed.assert_called_once()
