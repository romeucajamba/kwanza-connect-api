from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Room, RoomEvent, Message


@receiver(post_save, sender=Room)
def log_room_created(sender, instance, created, **kwargs):
    if created:
        RoomEvent.objects.create(
            room=instance,
            event_type='room_created',
            payload={'room_type': instance.room_type}
        )
        Message.objects.create(
            room=instance,
            sender_id=None,          # mensagem de sistema não tem remetente
            msg_type='system',
            content='Conversa iniciada.'
        )