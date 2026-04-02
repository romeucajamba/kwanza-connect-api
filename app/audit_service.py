from typing import Optional, Dict, Any
from audit.infra.repositories import DjangoAuditRepository
from audit.services.use_cases import RegisterAuditLogUseCase

# Singleton-like instance for global use
_audit_repo = DjangoAuditRepository()
_audit_use_case = RegisterAuditLogUseCase(_audit_repo)

def audit_log(action: str, resource: str, user_id=None, resource_id=None, metadata: Dict[str, Any] = None, request=None):
    """
    Helper global para registar auditoria. 
    Pode extrair IP e User-Agent do objeto 'request' se fornecido.
    """
    ip_address = None
    user_agent = None
    
    if request:
        # Tenta pegar o IP real se estiver atrás de um proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        # Se user_id não for passado mas o request tiver user autenticado
        if not user_id and hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id

    return _audit_use_case.execute(
        action=action,
        resource=resource,
        user_id=user_id,
        resource_id=resource_id,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )
