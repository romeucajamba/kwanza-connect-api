from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='offers.OfferInterest')
def on_interest_created(sender, instance, created, **kwargs):
    """Vendedor recebe notificação quando alguém clica em 'Tenho interesse'."""
    if not created:
        return

    from .service import NotificationService
    from .models  import NotificationType

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


@receiver(post_save, sender='offers.OfferInterest')
def on_interest_status_changed(sender, instance, created, **kwargs):
    """Comprador recebe notificação quando o vendedor aceita ou rejeita."""
    if created:
        return

    from .service import NotificationService
    from .models  import NotificationType

    if instance.status == 'chat_open':
        NotificationService.send(
            recipient         = instance.buyer,
            actor             = instance.offer.owner,
            notification_type = NotificationType.INTEREST_ACCEPTED,
            payload           = {
                'offer_id':  str(instance.offer.id),
                'room_id':   str(instance.room.id) if instance.room else None,
                'redirect':  f'/chat/{instance.room.id}' if instance.room else '/offers',
            },
        )

    elif instance.status == 'rejected':
        NotificationService.send(
            recipient         = instance.buyer,
            actor             = instance.offer.owner,
            notification_type = NotificationType.INTEREST_REJECTED,
            payload           = {
                'offer_id': str(instance.offer.id),
                'redirect': '/offers',
            },
        )

    elif instance.status == 'cancelled':
        NotificationService.send(
            recipient         = instance.offer.owner,
            actor             = instance.buyer,
            notification_type = NotificationType.INTEREST_CANCELLED,
            payload           = {
                'offer_id':    str(instance.offer.id),
                'interest_id': str(instance.id),
                'redirect':    f'/offers/{instance.offer.id}/interests',
            },
        )


@receiver(post_save, sender='chat.Message')
def on_new_message(sender, instance, created, **kwargs):
    """Membros da sala recebem notificação de nova mensagem."""
    if not created or instance.msg_type == 'system':
        return

    from .service import NotificationService
    from .models  import NotificationType

    members = instance.room.members.exclude(user=instance.sender).select_related('user')

    for member in members:
        NotificationService.send(
            recipient         = member.user,
            actor             = instance.sender,
            notification_type = NotificationType.NEW_MESSAGE,
            payload           = {
                'room_id':  str(instance.room.id),
                'preview':  instance.content[:60] if instance.content else '[ficheiro]',
                'redirect': f'/chat/{instance.room.id}',
            },
        )