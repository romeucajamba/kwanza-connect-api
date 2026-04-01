from celery import shared_task
from django.utils import timezone
from .models import Offer


@shared_task
def expire_old_offers():
    """
    Corre a cada hora via Celery Beat.
    Fecha ofertas cuja data de expiração já passou.
    """
    expired = Offer.objects.filter(
        status='active',
        expires_at__lt=timezone.now()
    )
    count = expired.update(status='expired')
    return f'{count} ofertas expiradas.'