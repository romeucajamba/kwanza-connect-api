from django.db import models
from django.conf import settings
import uuid

class AuditLog(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='audit_logs'
    )
    action      = models.CharField(max_length=255)
    resource    = models.CharField(max_length=255)
    resource_id = models.CharField(max_length=255, null=True, blank=True)
    metadata    = models.JSONField(default=dict, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registo de Auditoria'
        verbose_name_plural = 'Registos de Auditoria'

    def __str__(self):
        return f'{self.action} on {self.resource} by {self.user}'
