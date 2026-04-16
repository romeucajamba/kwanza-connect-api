from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Room, RoomEvent, Message


@receiver(post_save, sender=Room)
def log_room_created(sender, instance, created, **kwargs):
    """Log room creation and send the first system message."""
    if created:
        RoomEvent.objects.create(
            room=instance,
            event_type='room_created',
            payload={'room_type': instance.room_type}
        )
        # System messages don't have a human sender. 
        # Since we made Message.sender nullable, we can safely use None.
        Message.objects.create(
            room=instance,
            sender=None,
            msg_type='system',
            content='Conversa iniciada.'
        )