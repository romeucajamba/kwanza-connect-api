from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserSecurity


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    """Cria UserSecurity e NotificationPreference quando um utilizador é criado."""
    if not created:
        return

    # Segurança
    UserSecurity.objects.get_or_create(user=instance)

    # Preferências de notificação (importação tardia para evitar circular)
    try:
        from notifications.models import NotificationPreference
        NotificationPreference.objects.get_or_create(user=instance)
    except Exception:
        pass  # Módulo pode não estar disponível em migrações