from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import uuid

@dataclass
class TransactionEntity:
    id: uuid.UUID
    offer_id: Optional[uuid.UUID]
    room_id: Optional[uuid.UUID]
    seller_id: uuid.UUID
    buyer_id: uuid.UUID
    give_currency_id: uuid.UUID
    give_amount: Decimal
    want_currency_id: uuid.UUID
    want_amount: Decimal
    rate: Decimal
    status: str = 'completed'
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class TransactionReviewEntity:
    id: uuid.UUID
    transaction_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewed_id: uuid.UUID
    rating: int
    comment: str = ""
    created_at: Optional[datetime] = None
