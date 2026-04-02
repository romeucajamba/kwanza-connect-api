from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import AuditLogEntity
import uuid

class IAuditRepository(ABC):
    
    @abstractmethod
    def save(self, audit_log: AuditLogEntity) -> AuditLogEntity:
        """Salva um novo registo de auditoria."""
        pass
    
    @abstractmethod
    def get_by_user(self, user_id: uuid.UUID) -> List[AuditLogEntity]:
        """Retorna os logs associados a um utilizador."""
        pass
    
    @abstractmethod
    def get_by_resource(self, resource: str, resource_id: Optional[str] = None) -> List[AuditLogEntity]:
        """Retorna os logs associados a um recurso específico."""
        pass
