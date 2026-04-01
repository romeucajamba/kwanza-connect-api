"""Domain entities do módulo de notificações."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class NotificationEntity:
    id:          str
    recipient_id: str
    actor_id:     Optional[str]
    type:        str
    title:       str
    body:        str
    payload:     Dict
    is_read:     bool
    read_at:     Optional[datetime]
    created_at:  datetime


@dataclass
class NotificationPreferenceEntity:
    user_id:              str
    channel:              str
    new_interest:        bool
    interest_accepted:   bool
    interest_rejected:   bool
    interest_cancelled:  bool
    offer_expired:       bool
    new_message:         bool
    deal_accepted:       bool
    deal_cancelled:      bool
    rate_alert:          bool
    account_verified:    bool
    system:              bool
