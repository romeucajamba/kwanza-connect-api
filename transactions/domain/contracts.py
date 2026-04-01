"""Contratos do módulo de transações."""
from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import TransactionEntity, TransactionReviewEntity


class ITransactionRepository(ABC):

    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Optional[TransactionEntity]:
        ...

    @abstractmethod
    def list_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[TransactionEntity]:
        ...

    @abstractmethod
    def create(self, **data) -> TransactionEntity:
        ...

    @abstractmethod
    def update_status(self, transaction_id: str, status: str) -> None:
        ...


class ITransactionReviewRepository(ABC):

    @abstractmethod
    def get_by_transaction(self, transaction_id: str) -> List[TransactionReviewEntity]:
        ...

    @abstractmethod
    def create(self, **data) -> TransactionReviewEntity:
        ...
        
    @abstractmethod
    def get_average_rating(self, user_id: str) -> float:
        ...
