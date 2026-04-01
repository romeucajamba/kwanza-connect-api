import secrets
import hashlib
from django.db import models
from django.utils import timezone


class APIKey(models.Model):
    """
    Representa uma chave de acesso para clientes da API (Frontend, Mobile, etc).
    A chave real não é armazenada; apenas o seu hash SHA-256.
    """
    name       = models.CharField(max_length=100, unique=True, help_text="Nome do cliente/serviço (ex: Mobile App)")
    prefix     = models.CharField(max_length=16, unique=True, editable=False)
    hashed_key = models.CharField(max_length=64, editable=False)
    
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Chave de API"
        verbose_name_plural = "Chaves de API"

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    @classmethod
    def generate(cls, name, expires_at=None):
        """Gera uma nova chave e retorna (object, raw_key)."""
        prefix  = secrets.token_hex(4) # 8 chars
        secret  = secrets.token_urlsafe(32)
        raw_key = f"kc_{prefix}.{secret}"
        
        hashed  = hashlib.sha256(raw_key.encode()).hexdigest()
        
        obj = cls.objects.create(
            name=name,
            prefix=prefix,
            hashed_key=hashed,
            expires_at=expires_at
        )
        return obj, raw_key

    def verify(self, raw_key):
        """Verifica se a chave fornecida é válida."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        match = hashlib.sha256(raw_key.encode()).hexdigest() == self.hashed_key
        if match:
            self.last_used = timezone.now()
            self.save(update_fields=['last_used'])
        return match
