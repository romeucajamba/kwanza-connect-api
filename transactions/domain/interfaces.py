from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import TransactionEntity, TransactionReviewEntity
import uuid

class ITransactionRepository(ABC):
    
    @abstractmethod
    def save_transaction(self, transaction: TransactionEntity) -> TransactionEntity:
        pass

    @abstractmethod
    def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[TransactionEntity]:
        pass

    @abstractmethod
    def list_user_transactions(self, user_id: uuid.UUID) -> List[TransactionEntity]:
        pass

    @abstractmethod
    def save_review(self, review: TransactionReviewEntity) -> TransactionReviewEntity:
        pass

    @abstractmethod
    def get_review_by_transaction_and_user(self, transaction_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TransactionReviewEntity]:
        pass

    @abstractmethod
    def list_user_reviews_received(self, user_id: uuid.UUID) -> List[TransactionReviewEntity]:
        pass
