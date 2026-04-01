"""
Domain entities para o módulo users.
Dataclasses puras — sem dependência de Django/ORM.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id:                  str
    email:               str
    full_name:           str
    phone:               str = ''
    country_code:        str = 'AO'
    city:                str = ''
    bio:                 str = ''
    is_active:           bool = False
    is_verified:         bool = False
    is_available:        bool = False
    verification_status: str = 'pending'
    preferred_give_currency: str = ''
    preferred_want_currency: str = ''
    date_joined:         Optional[datetime] = None
    last_seen:           Optional[datetime] = None
    avatar_url:          Optional[str] = None


@dataclass
class UserSecurityEntity:
    id:                   str
    user_id:              str
    email_verified:       bool = False
    phone_verified:       bool = False
    two_factor_enabled:   bool = False
    failed_login_attempts: int = 0
    is_locked:            bool = False
