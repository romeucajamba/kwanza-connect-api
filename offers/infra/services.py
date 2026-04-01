import uuid
from ..services.use_cases import IChatService, INotificationService

class DjangoChatService(IChatService):
    def create_offer_room(self, offer_id: uuid.UUID, owner_id: uuid.UUID, buyer_id: uuid.UUID) -> uuid.UUID:
        from chat.models import Room, RoomMember, RoomEvent
        
        room = Room.objects.create(
            offer_id=offer_id,
            room_type='offer',
            status='active',
        )
        RoomMember.objects.create(room=room, user_id=owner_id, is_admin=True)
        RoomMember.objects.create(room=room, user_id=buyer_id)
        
        RoomEvent.objects.create(
            room=room,
            actor_id=owner_id,
            event_type='room_created',
            payload={'offer_id': str(offer_id)}
        )
        return room.id

class DjangoNotificationService(INotificationService):
    def notify_interest_accepted(self, buyer_id: uuid.UUID, offer_id: uuid.UUID, room_id: uuid.UUID) -> None:
        from notifications.models import Notification
        Notification.objects.create(
            user_id=buyer_id,
            type='interest_accepted',
            payload={
                'offer_id': str(offer_id),
                'room_id':  str(room_id),
                'message':  'O seu interesse foi aceite.',
            }
        )

    def notify_interest_rejected(self, buyer_id: uuid.UUID, offer_id: uuid.UUID) -> None:
        from notifications.models import Notification
        Notification.objects.create(
            user_id=buyer_id,
            type='interest_rejected',
            payload={
                'offer_id': str(offer_id),
                'message':  'O seu interesse foi rejeitado.',
            }
        )
