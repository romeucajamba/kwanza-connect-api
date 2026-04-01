import uuid
from ..services.use_cases import IOfferService, IChatService, INotificationService
from app.services.websocket_service import ChannelsWebSocketService

class DjangoOfferService(IOfferService):
    def close_offer(self, offer_id: uuid.UUID) -> None:
        from offers.models import Offer
        Offer.objects.filter(id=offer_id).update(status='closed')

    def get_offer_details(self, offer_id: uuid.UUID) -> dict:
        from offers.models import Offer
        try:
            offer = Offer.objects.get(id=offer_id)
            return {
                'id': offer.id,
                'owner_id': offer.owner_id,
                'give_currency_id': offer.give_currency_id,
                'give_amount': offer.give_amount,
                'want_currency_id': offer.want_currency_id,
                'want_amount': offer.want_amount,
                'exchange_rate_snapshot': offer.exchange_rate_snapshot
            }
        except Offer.DoesNotExist:
            return {}

class DjangoChatService(IChatService):
    def close_room(self, room_id: uuid.UUID) -> None:
        from chat.models import Room
        from django.utils import timezone
        Room.objects.filter(id=room_id).update(status='closed', closed_at=timezone.now())

    def get_other_participant(self, room_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        from chat.models import RoomMember
        member = RoomMember.objects.filter(room_id=room_id).exclude(user_id=user_id).first()
        return member.user_id if member else None

    def verify_room_offer(self, room_id: uuid.UUID, offer_id: uuid.UUID) -> bool:
        from chat.models import Room
        return Room.objects.filter(id=room_id, offer_id=offer_id).exists()

class DjangoNotificationService(INotificationService):
    def __init__(self):
        self.ws_service = ChannelsWebSocketService()

    def notify_transaction_completed(self, recipient_id: uuid.UUID, actor_id: uuid.UUID, tx_id: uuid.UUID) -> None:
        from notifications.models import Notification
        Notification.objects.create(
            recipient_id=recipient_id,
            actor_id=actor_id,
            type='system',
            title='Troca concluída',
            body='Uma troca foi marcada como concluída.',
            payload={'transaction_id': str(tx_id), 'redirect': f'/transactions/{tx_id}'}
        )
        self.ws_service.send_to_user(str(recipient_id), "new_notification", {"type": "tx_completed", "id": str(tx_id)})

    def notify_new_review(self, recipient_id: uuid.UUID, actor_id: uuid.UUID, rating: int) -> None:
        from notifications.models import Notification
        Notification.objects.create(
            recipient_id=recipient_id,
            actor_id=actor_id,
            type='system',
            title='Nova avaliação',
            body=f'Recebeste uma avaliação de {rating} estrelas.',
            payload={'redirect': '/profile/reviews'}
        )
        self.ws_service.send_to_user(str(recipient_id), "new_notification", {"type": "new_review", "rating": rating})
