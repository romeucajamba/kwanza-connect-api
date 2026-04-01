from rest_framework import permissions
from .models import APIKey


class HasAPIKey(permissions.BasePermission):
    """
    Permissão que exige a chave de API no header X-API-KEY.
    """
    message = "Acesso negado. Chave de API inválida ou em falta no header X-API-KEY."

    def has_permission(self, request, view):
        raw_key = request.META.get('HTTP_X_API_KEY')
        if not raw_key:
            return False
        
        # O formato da chave é: kc_prefix.secret
        try:
            prefix = raw_key.split('.')[0].replace('kc_', '')
            key_obj = APIKey.objects.get(prefix=prefix, is_active=True)
            return key_obj.verify(raw_key)
        except (APIKey.DoesNotExist, IndexError, ValueError):
            return False
