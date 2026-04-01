"""Domain entities do módulo chat."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class RoomEntity:
    id:          str
    offer_id:    Optional[str]
    room_type:   str
    status:      str
    created_at:  datetime
    closed_at:   Optional[datetime]


@dataclass
class RoomMemberEntity:
    id:           str
    room_id:      str
    user_id:      str
    is_admin:     bool
    joined_at:    datetime
    last_read_at: Optional[datetime]


@dataclass
class MessageEntity:
    id:          str
    room_id:     str
    sender_id:   str
    reply_to_id: Optional[str]
    msg_type:    str
    content:     str
    file_url:    Optional[str]
    file_name:   Optional[str]
    file_size:   Optional[int]
    is_deleted:  bool
    is_edited:   bool
    created_at:  datetime
    edited_at:   Optional[datetime]
