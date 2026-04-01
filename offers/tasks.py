from celery import shared_task
from django.utils import timezone


@shared_task
def expire_old_offers():
    """
    Corre a cada hora via Celery Beat.
    Fecha ofertas cuja data de expiração já passou e notifica o dono.
    """
    from .models import Offer

    expired_qs = Offer.objects.filter(
        status='active',
        expires_at__lt=timezone.now(),
    ).select_related('owner', 'give_currency', 'want_currency')

    count = 0
    for offer in expired_qs:
        offer.status = 'expired'
        offer.save(update_fields=['status', 'updated_at'])
        count += 1

        # Notifica o dono
        try:
            from notifications.services.notification_service import NotificationService
            from notifications.models import NotificationType
            NotificationService.send(
                recipient         = offer.owner,
                notification_type = NotificationType.OFFER_EXPIRED,
                payload           = {
                    'offer_id':      str(offer.id),
                    'give_amount':   str(offer.give_amount),
                    'give_currency': offer.give_currency.code,
                    'redirect':      f'/offers/{offer.id}',
                },
            )
        except Exception:
            pass

    return f'{count} oferta(s) expirada(s).'