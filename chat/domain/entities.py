from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

@dataclass
class RoomEntity:
    id: uuid.UUID
    offer_id: Optional[uuid.UUID] = None
    room_type: str = 'direct'
    status: str = 'active'
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    def is_active(self) -> bool:
        return self.status == 'active'

@dataclass
class RoomMemberEntity:
    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    is_admin: bool = False
    joined_at: Optional[datetime] = None
    last_read_at: Optional[datetime] = None

@dataclass
class MessageEntity:
    id: uuid.UUID
    room_id: uuid.UUID
    sender_id: uuid.UUID
    msg_type: str = 'text'
    content: str = ""
    file: Optional[str] = None
    file_name: str = ""
    file_size: Optional[int] = None
    reply_to_id: Optional[uuid.UUID] = None
    is_deleted: bool = False
    is_edited: bool = False
    created_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None

@dataclass
class MessageReadEntity:
    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    read_at: datetime

@dataclass
class MessageReactionEntity:
    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    emoji: str
    created_at: Optional[datetime] = None

@dataclass
class RoomEventEntity:
    id: uuid.UUID
    room_id: uuid.UUID
    actor_id: Optional[uuid.UUID]
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
