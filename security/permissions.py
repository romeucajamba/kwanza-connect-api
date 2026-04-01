from rest_framework import permissions
from .infra.repositories import DjangoSecurityRepository
from .services.use_cases import VerifyAPIKeyUseCase

class HasAPIKey(permissions.BasePermission):
    """
    Permissão que exige a chave de API no header X-API-KEY.
    Refatorado para usar Clean Architecture (Use Cases).
    """
    message = "Acesso negado. Chave de API inválida ou em falta no header X-API-KEY."

    def has_permission(self, request, view):
        raw_key = request.META.get('HTTP_X_API_KEY')
        if not raw_key:
            return False
        
        repo = DjangoSecurityRepository()
        use_case = VerifyAPIKeyUseCase(repo)
        return use_case.execute(raw_key)
