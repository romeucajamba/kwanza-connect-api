from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import OfferEntity, OfferInterestEntity, CurrencyEntity, ExchangeRateEntity
import uuid

class IOfferRepository(ABC):
    
    @abstractmethod
    def get_currency_by_code(self, code: str) -> Optional[CurrencyEntity]:
        pass
    
    @abstractmethod
    def get_currency_by_id(self, currency_id: uuid.UUID) -> Optional[CurrencyEntity]:
        pass

    @abstractmethod
    def get_exchange_rate(self, from_id: uuid.UUID, to_id: uuid.UUID) -> Optional[ExchangeRateEntity]:
        pass

    @abstractmethod
    def save_offer(self, offer: OfferEntity) -> OfferEntity:
        pass

    @abstractmethod
    def get_offer_by_id(self, offer_id: uuid.UUID) -> Optional[OfferEntity]:
        pass

    @abstractmethod
    def get_offer_by_id_for_update(self, offer_id: uuid.UUID) -> Optional[OfferEntity]:
        pass

    @abstractmethod
    def list_offers(self, filters: dict) -> List[OfferEntity]:
        pass

    @abstractmethod
    def save_interest(self, interest: OfferInterestEntity) -> OfferInterestEntity:
        pass

    @abstractmethod
    def get_interest_by_id(self, interest_id: uuid.UUID) -> Optional[OfferInterestEntity]:
        pass

    @abstractmethod
    def get_interest_by_id_for_update(self, interest_id: uuid.UUID) -> Optional[OfferInterestEntity]:
        pass

    @abstractmethod
    def get_interest_by_offer_and_buyer(self, offer_id: uuid.UUID, buyer_id: uuid.UUID) -> Optional[OfferInterestEntity]:
        pass

    @abstractmethod
    def increment_offer_views(self, offer_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    def register_offer_view(self, offer_id: uuid.UUID, user_id: Optional[uuid.UUID]) -> None:
        pass
