"""
Use cases do módulo rates.
"""
from decimal import Decimal
from rest_framework.exceptions import ValidationError, NotFound
from offers.models import Currency, ExchangeRate


class GetLiveRateUseCase:
    def execute(self, from_code: str, to_code: str) -> Decimal:
        try:
            from_currency = Currency.objects.get(code=from_code.upper(), is_active=True)
            to_currency   = Currency.objects.get(code=to_code.upper(), is_active=True)
        except Currency.DoesNotExist:
            raise NotFound('Moeda não encontrada ou inactiva.')

        try:
            rate_obj = ExchangeRate.objects.get(
                from_currency=from_currency,
                to_currency=to_currency
            )
            return rate_obj.rate
        except ExchangeRate.DoesNotExist:
            raise NotFound(f'Taxa de câmbio não disponível para {from_code}/{to_code}.')


class ConvertAmountUseCase:
    def execute(self, from_code: str, to_code: str, amount: Decimal) -> dict:
        if amount <= 0:
            raise ValidationError('O valor deve ser positivo.')

        rate = GetLiveRateUseCase().execute(from_code, to_code)
        converted_amount = amount * rate

        return {
            'from_currency': from_code.upper(),
            'to_currency':   to_code.upper(),
            'amount':        amount,
            'rate':          rate,
            'converted_amount': converted_amount
        }


class GetPlatformStatsUseCase:
    def execute(self) -> dict:
        """
        Retorna estatísticas simples da plataforma.
        Moedas mais procuradas, convertidas, etc.
        """
        from offers.models import Offer
        from django.db.models import Count

        # Moedas mais oferecidas (give_currency)
        top_give = Offer.objects.values('give_currency__code')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:5]

        # Moedas mais procuradas (want_currency)
        top_want = Offer.objects.values('want_currency__code')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:5]

        return {
            'top_give_currencies': list(top_give),
            'top_want_currencies': list(top_want),
        }
