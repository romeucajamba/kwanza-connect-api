import secrets
import hashlib
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'prefix', 'is_active', 'last_used', 'created_at']
    list_filter   = ['is_active', 'created_at']
    search_fields = ['name', 'prefix']
    readonly_fields = ['prefix', 'hashed_key', 'last_used', 'created_at']

    def save_model(self, request, obj, form, change):
        if not change:
            # Ao criar, geramos a chave e mostramos ao administrador
            obj, raw_key = APIKey.generate(name=obj.name, expires_at=obj.expires_at)
            self.message_user(
                request, 
                mark_safe(f"<h3>⚠️ CHAVE GERADA (GUARTA ESTA CHAVE AGORA):</h3><br><b>{raw_key}</b><br><br>Esta chave nunca mais será exibida.")
            )
        else:
            super().save_model(request, obj, form, change)
