from typing import Optional, List, Dict
from decimal import Decimal
from django.db.models import Count
from offers.models import ExchangeRate, Currency, Offer
from users.models import User
from .domain.entities import PlatformStatsEntity
from .domain.interfaces import IRatesRepository

class DjangoRatesRepository(IRatesRepository):
    
    def get_exchange_rate(self, from_code: str, to_code: str) -> Optional[Decimal]:
        try:
            rate = ExchangeRate.objects.get(
                from_currency__code__iexact=from_code,
                to_currency__code__iexact=to_code
            )
            return rate.rate
        except ExchangeRate.DoesNotExist:
            return None

    def get_platform_stats(self) -> PlatformStatsEntity:
        active_offers = Offer.objects.filter(status='active').count()
        total_users = User.objects.filter(is_active=True).count()
        # simplified successful_deals as dealing status for now
        successful_deals = Offer.objects.filter(status='dealing').count()
        
        # simplified top_currencies as sorting by code
        top_currencies = list(Currency.objects.filter(is_active=True).values_list('code', flat=True)[:5])
        
        return PlatformStatsEntity(
            active_offers=active_offers,
            total_users=total_users,
            successful_deals=successful_deals,
            top_currencies=top_currencies
        )

    def list_all_rates(self) -> List[Dict]:
        rates = ExchangeRate.objects.select_related('from_currency', 'to_currency').all()
        return [{
            'from': r.from_currency.code,
            'to': r.to_currency.code,
            'rate': r.rate,
            'fetched_at': r.fetched_at
        } for r in rates]
