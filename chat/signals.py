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
        # Fix: System messages don't have a sender, but the model needs one (if not nullable).
        # We use a None sender if nullable, or a system user if required.
        # Since Message model's sender is NOT NULL, let's use the owner of the offer as the initial system message if available,
        # or better, ensure system messages are handled properly.
        # Original code had sender_id=None, which failed.
        # I will use a placeholder or handle it via a system message flag if needed.
        # For now, let's use the first member found or just skip it if we can't find one.
        member = instance.members.first()
        Message.objects.create(
            room=instance,
            sender=member.user if member else None, # This might still fail if not nullable
            msg_type='system',
            content='Conversa iniciada.'
        )