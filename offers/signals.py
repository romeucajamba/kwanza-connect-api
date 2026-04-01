from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Offer, OfferInterest
from notifications.models import Notification


@receiver(post_save, sender=OfferInterest)
def notify_owner_new_interest(sender, instance, created, **kwargs):
    """Notifica o dono da oferta quando alguém demonstra interesse."""
    if created:
        Notification.objects.create(
            user=instance.offer.owner,
            type='new_interest',
            payload={
                'offer_id':   str(instance.offer.id),
                'buyer_id':   str(instance.buyer.id),
                'buyer_name': instance.buyer.full_name,
                'message':    instance.message,
            }
        )