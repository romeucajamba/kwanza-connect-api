from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class APIKeyEntity:
    id: int # Django using auto-int ID for this one in models.py
    name: str
    prefix: str
    hashed_key: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.now():
            return False
        return True
