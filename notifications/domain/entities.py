from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

@dataclass
class NotificationEntity:
    id: uuid.UUID
    recipient_id: uuid.UUID
    type: str
    title: str
    body: str
    actor_id: Optional[uuid.UUID] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    is_read: bool = False
    read_at: Optional[datetime] = None
    is_sent_ws: bool = False
    is_sent_email: bool = False
    is_sent_push: bool = False
    created_at: Optional[datetime] = None

@dataclass
class NotificationPreferenceEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    channel: str = 'in_app'
    new_interest: bool = True
    interest_accepted: bool = True
    interest_rejected: bool = True
    interest_cancelled: bool = True
    offer_expired: bool = True
    new_message: bool = True
    deal_accepted: bool = True
    deal_cancelled: bool = True
    rate_alert: bool = False
    account_verified: bool = True
    system: bool = True

    def allows(self, notification_type: str) -> bool:
        return getattr(self, notification_type, True)

@dataclass
class PushDeviceEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    token: str
    device_name: str = ""
    is_active: bool = True
    registered_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
