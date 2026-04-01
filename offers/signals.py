"""
Signals do módulo offers.
Corrigido: usa 'recipient' (não 'user') e NotificationService.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OfferInterest


@receiver(post_save, sender=OfferInterest)
def on_interest_created(sender, instance, created, **kwargs):
    """Notifica o dono da oferta quando alguém demonstra interesse."""
    if not created:
        return
    try:
        from notifications.services.notification_service import NotificationService
        from notifications.models import NotificationType
        NotificationService.send(
            recipient         = instance.offer.owner,
            actor             = instance.buyer,
            notification_type = NotificationType.NEW_INTEREST,
            payload           = {
                'offer_id':      str(instance.offer.id),
                'interest_id':   str(instance.id),
                'give_amount':   str(instance.offer.give_amount),
                'give_currency': instance.offer.give_currency.code,
                'want_currency': instance.offer.want_currency.code,
                'redirect':      f'/offers/{instance.offer.id}/interests',
            },
        )
    except Exception:
        pass  # Não falhar a operação principal por erro de notificação