from typing import Optional, List
import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import (
    Currency as DjangoCurrency, 
    ExchangeRate as DjangoExchangeRate, 
    Offer as DjangoOffer, 
    OfferInterest as DjangoOfferInterest,
    OfferView as DjangoOfferView
)
from ..domain.entities import OfferEntity, OfferInterestEntity, CurrencyEntity, ExchangeRateEntity
from ..domain.interfaces import IOfferRepository

class DjangoOfferRepository(IOfferRepository):
    
    def _currency_to_entity(self, django_currency: DjangoCurrency) -> CurrencyEntity:
        return CurrencyEntity(
            id=django_currency.id,
            code=django_currency.code,
            name=django_currency.name,
            symbol=django_currency.symbol,
            flag_emoji=django_currency.flag_emoji,
            is_active=django_currency.is_active,
            sort_order=django_currency.sort_order
        )

    def _exchange_rate_to_entity(self, django_rate: DjangoExchangeRate) -> ExchangeRateEntity:
        return ExchangeRateEntity(
            id=django_rate.id,
            from_currency_id=django_rate.from_currency_id,
            to_currency_id=django_rate.to_currency_id,
            rate=django_rate.rate,
            source=django_rate.source,
            fetched_at=django_rate.fetched_at
        )

    def _offer_to_entity(self, django_offer: DjangoOffer) -> OfferEntity:
        return OfferEntity(
            id=django_offer.id,
            owner_id=django_offer.owner_id,
            give_currency_id=django_offer.give_currency_id,
            give_amount=django_offer.give_amount,
            want_currency_id=django_offer.want_currency_id,
            want_amount=django_offer.want_amount,
            exchange_rate_snapshot=django_offer.exchange_rate_snapshot,
            offer_type=django_offer.offer_type,
            status=django_offer.status,
            notes=django_offer.notes,
            views_count=django_offer.views_count,
            city=django_offer.city,
            country_code=django_offer.country_code,
            implied_rate=django_offer.implied_rate,
            expires_at=django_offer.expires_at,
            created_at=django_offer.created_at,
            updated_at=django_offer.updated_at
        )

    def _interest_to_entity(self, django_interest: DjangoOfferInterest) -> OfferInterestEntity:
        return OfferInterestEntity(
            id=django_interest.id,
            offer_id=django_interest.offer_id,
            buyer_id=django_interest.buyer_id,
            status=django_interest.status,
            message=django_interest.message,
            room_id=django_interest.room_id,
            created_at=django_interest.created_at,
            responded_at=django_interest.responded_at
        )

    def get_currency_by_code(self, code: str) -> Optional[CurrencyEntity]:
        try:
            return self._currency_to_entity(DjangoCurrency.objects.get(code=code))
        except DjangoCurrency.DoesNotExist:
            return None

    def get_currency_by_id(self, currency_id: uuid.UUID) -> Optional[CurrencyEntity]:
        try:
            return self._currency_to_entity(DjangoCurrency.objects.get(id=currency_id))
        except DjangoCurrency.DoesNotExist:
            return None

    def get_exchange_rate(self, from_id: uuid.UUID, to_id: uuid.UUID) -> Optional[ExchangeRateEntity]:
        try:
            rate = DjangoExchangeRate.objects.get(from_currency_id=from_id, to_currency_id=to_id)
            return self._exchange_rate_to_entity(rate)
        except DjangoExchangeRate.DoesNotExist:
            return None

    def save_offer(self, offer: OfferEntity) -> OfferEntity:
        with transaction.atomic():
            django_offer, created = DjangoOffer.objects.update_or_create(
                id=offer.id,
                defaults={
                    'owner_id': offer.owner_id,
                    'give_currency_id': offer.give_currency_id,
                    'give_amount': offer.give_amount,
                    'want_currency_id': offer.want_currency_id,
                    'want_amount': offer.want_amount,
                    'exchange_rate_snapshot': offer.exchange_rate_snapshot,
                    'offer_type': offer.offer_type,
                    'status': offer.status,
                    'notes': offer.notes,
                    'views_count': offer.views_count,
                    'city': offer.city,
                    'country_code': offer.country_code,
                    'expires_at': offer.expires_at,
                }
            )
            return self._offer_to_entity(django_offer)

    def get_offer_by_id(self, offer_id: uuid.UUID) -> Optional[OfferEntity]:
        try:
            return self._offer_to_entity(DjangoOffer.objects.get(id=offer_id))
        except DjangoOffer.DoesNotExist:
            return None

    def list_offers(self, filters: dict) -> List[OfferEntity]:
        qs = DjangoOffer.objects.filter(status='active').select_related('owner', 'give_currency', 'want_currency')
        if give := filters.get('give_currency'):
            qs = qs.filter(give_currency__code__iexact=give)
        if want := filters.get('want_currency'):
            qs = qs.filter(want_currency__code__iexact=want)
        if city := filters.get('city'):
            qs = qs.filter(city__icontains=city)
        if min_amount := filters.get('min_amount'):
            qs = qs.filter(give_amount__gte=min_amount)
        if max_amount := filters.get('max_amount'):
            qs = qs.filter(give_amount__lte=max_amount)
        
        # Exclude expired
        final_qs = qs.exclude(expires_at__lt=timezone.now())
        return [self._offer_to_entity(o) for o in final_qs]

    def save_interest(self, interest: OfferInterestEntity) -> OfferInterestEntity:
        django_interest, created = DjangoOfferInterest.objects.update_or_create(
            id=interest.id,
            defaults={
                'offer_id': interest.offer_id,
                'buyer_id': interest.buyer_id,
                'status': interest.status,
                'message': interest.message,
                'room_id': interest.room_id,
                'responded_at': interest.responded_at,
            }
        )
        return self._interest_to_entity(django_interest)

    def get_interest_by_id(self, interest_id: uuid.UUID) -> Optional[OfferInterestEntity]:
        try:
            return self._interest_to_entity(DjangoOfferInterest.objects.get(id=interest_id))
        except DjangoOfferInterest.DoesNotExist:
            return None

    def get_interest_by_offer_and_buyer(self, offer_id: uuid.UUID, buyer_id: uuid.UUID) -> Optional[OfferInterestEntity]:
        try:
            return self._interest_to_entity(DjangoOfferInterest.objects.get(offer_id=offer_id, buyer_id=buyer_id))
        except DjangoOfferInterest.DoesNotExist:
            return None

    def increment_offer_views(self, offer_id: uuid.UUID) -> None:
        DjangoOffer.objects.filter(id=offer_id).update(views_count=models.F('views_count') + 1)

    def register_offer_view(self, offer_id: uuid.UUID, user_id: Optional[uuid.UUID]) -> None:
        DjangoOfferView.objects.create(offer_id=offer_id, user_id=user_id)
