"""
Use cases do módulo offers.
"""
from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from ..models import Offer, OfferInterest, Currency, ExchangeRate


def _get_current_rate(give_currency, want_currency) -> float:
    """Obtém a taxa de câmbio actual entre dois pares de moedas."""
    try:
        rate_obj = ExchangeRate.objects.get(
            from_currency=give_currency,
            to_currency=want_currency,
        )
        return float(rate_obj.rate)
    except ExchangeRate.DoesNotExist:
        return 0.0


class CreateOfferUseCase:
    def execute(self, user, data: dict) -> Offer:
        give_currency = data.get('give_currency')
        want_currency = data.get('want_currency')

        if not give_currency or not want_currency:
            raise ValidationError('Moedas de origem e destino são obrigatórias.')
        if give_currency == want_currency:
            raise ValidationError('As moedas de origem e destino não podem ser iguais.')

        # Snapshot da taxa real no momento da publicação
        rate_snapshot = _get_current_rate(give_currency, want_currency)

        offer = Offer.objects.create(
            owner=user,
            give_currency=give_currency,
            give_amount=data['give_amount'],
            want_currency=want_currency,
            want_amount=data['want_amount'],
            exchange_rate_snapshot=rate_snapshot,
            offer_type=data.get('offer_type', 'sell'),
            notes=data.get('notes', ''),
            city=data.get('city', user.city),
            country_code=data.get('country_code', user.country_code),
            expires_at=data.get('expires_at'),
        )
        return offer


class ListOffersUseCase:
    def execute(self, filters: dict):
        qs = Offer.objects.select_related('owner', 'give_currency', 'want_currency').filter(
            status='active'
        )
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
        return qs.exclude(expires_at__lt=timezone.now())


class GetOfferUseCase:
    def execute(self, offer_id: str, viewer=None) -> Offer:
        try:
            offer = Offer.objects.select_related(
                'owner', 'give_currency', 'want_currency'
            ).get(id=offer_id)
        except Offer.DoesNotExist:
            raise NotFound('Oferta não encontrada.')

        # Regista visualização (apenas por utilizadores que não são o dono)
        if viewer and viewer != offer.owner:
            from ..models import OfferView
            OfferView.objects.get_or_create(offer=offer, user=viewer)
            Offer.objects.filter(id=offer_id).update(views_count=offer.views_count + 1)
            offer.views_count += 1

        return offer


class PauseOfferUseCase:
    def execute(self, user, offer_id: str) -> Offer:
        offer = self._get_owned_offer(user, offer_id)
        if offer.status not in ('active',):
            raise ValidationError('Só é possível pausar ofertas activas.')
        offer.pause()
        return offer

    def _get_owned_offer(self, user, offer_id: str) -> Offer:
        try:
            return Offer.objects.get(id=offer_id, owner=user)
        except Offer.DoesNotExist:
            raise NotFound('Oferta não encontrada ou não pertence ao utilizador.')


class ResumeOfferUseCase(PauseOfferUseCase):
    def execute(self, user, offer_id: str) -> Offer:
        offer = self._get_owned_offer(user, offer_id)
        if offer.status not in ('paused',):
            raise ValidationError('Só é possível retomar ofertas pausadas.')
        offer.resume()
        return offer


class CloseOfferUseCase(PauseOfferUseCase):
    def execute(self, user, offer_id: str) -> Offer:
        offer = self._get_owned_offer(user, offer_id)
        offer.close()
        return offer


class ExpressInterestUseCase:
    def execute(self, user, offer_id: str, message: str = '') -> OfferInterest:
        try:
            offer = Offer.objects.select_related('owner').get(id=offer_id)
        except Offer.DoesNotExist:
            raise NotFound('Oferta não encontrada.')

        if offer.owner == user:
            raise ValidationError('Não pode demonstrar interesse na sua própria oferta.')
        if not offer.is_active:
            raise ValidationError('Esta oferta já não está disponível.')
        if OfferInterest.objects.filter(offer=offer, buyer=user).exists():
            raise ValidationError('Já demonstrou interesse nesta oferta.')

        interest = OfferInterest.objects.create(
            offer=offer,
            buyer=user,
            message=message,
        )
        return interest


class AcceptInterestUseCase:
    def execute(self, user, interest_id: str):
        try:
            interest = OfferInterest.objects.select_related(
                'offer__owner', 'offer__give_currency', 'offer__want_currency', 'buyer'
            ).get(id=interest_id)
        except OfferInterest.DoesNotExist:
            raise NotFound('Interesse não encontrado.')

        if interest.offer.owner != user:
            raise PermissionDenied('Apenas o dono da oferta pode aceitar interesses.')

        room = interest.accept(accepted_by=user)
        return room


class RejectInterestUseCase:
    def execute(self, user, interest_id: str) -> None:
        try:
            interest = OfferInterest.objects.select_related('offer__owner').get(id=interest_id)
        except OfferInterest.DoesNotExist:
            raise NotFound('Interesse não encontrado.')

        if interest.offer.owner != user:
            raise PermissionDenied('Apenas o dono da oferta pode rejeitar interesses.')
        interest.reject(rejected_by=user)


class CancelInterestUseCase:
    def execute(self, user, interest_id: str) -> None:
        try:
            interest = OfferInterest.objects.get(id=interest_id, buyer=user)
        except OfferInterest.DoesNotExist:
            raise NotFound('Interesse não encontrado.')
        interest.cancel(cancelled_by=user)
