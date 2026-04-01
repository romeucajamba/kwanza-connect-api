"""Domain entities para o módulo offers."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class CurrencyEntity:
    id:         str
    code:       str
    name:       str
    symbol:     str
    flag_emoji: str
    is_active:  bool


@dataclass
class OfferEntity:
    id:                      str
    owner_id:                str
    give_currency_code:      str
    give_amount:             Decimal
    want_currency_code:      str
    want_amount:             Decimal
    exchange_rate_snapshot:  Decimal
    implied_rate:            Optional[Decimal]
    offer_type:              str
    status:                  str
    notes:                   str
    city:                    str
    country_code:            str
    views_count:             int
    created_at:              Optional[datetime]
    expires_at:              Optional[datetime]


@dataclass
class OfferInterestEntity:
    id:          str
    offer_id:    str
    buyer_id:    str
    status:      str
    message:     str
    room_id:     Optional[str]
    created_at:  Optional[datetime]
