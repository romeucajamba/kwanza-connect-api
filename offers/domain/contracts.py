"""Contratos do módulo offers."""
from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import OfferEntity, OfferInterestEntity


class IOfferRepository(ABC):

    @abstractmethod
    def get_by_id(self, offer_id: str) -> Optional[OfferEntity]:
        ...

    @abstractmethod
    def list_active(self, filters: dict) -> List[OfferEntity]:
        ...

    @abstractmethod
    def create(self, **data) -> OfferEntity:
        ...

    @abstractmethod
    def update_status(self, offer_id: str, status: str) -> None:
        ...


class IOfferInterestRepository(ABC):

    @abstractmethod
    def get_by_id(self, interest_id: str) -> Optional[OfferInterestEntity]:
        ...

    @abstractmethod
    def create(self, offer_id: str, buyer_id: str, message: str) -> OfferInterestEntity:
        ...

    @abstractmethod
    def list_by_offer(self, offer_id: str) -> List[OfferInterestEntity]:
        ...
