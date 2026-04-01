"""Domain entities do módulo de transações."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class TransactionEntity:
    id:           str
    offer_id:     Optional[str]
    room_id:      Optional[str]
    seller_id:    str
    buyer_id:     str
    give_currency_code: str
    give_amount:  Decimal
    want_currency_code: str
    want_amount:  Decimal
    rate:         Decimal
    status:       str
    notes:        str
    created_at:   datetime
    updated_at:   Optional[datetime]


@dataclass
class TransactionReviewEntity:
    id:             str
    transaction_id: str
    reviewer_id:    str
    reviewed_id:    str
    rating:         int
    comment:        str
    created_at:     datetime
