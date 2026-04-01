"""
Use cases do módulo de segurança.
Responsável pela geração e verificação de chaves de API.
"""
import secrets
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Tuple
from ..domain.entities import APIKeyEntity
from ..domain.interfaces import ISecurityRepository

class GenerateAPIKeyUseCase:
    def __init__(self, repository: ISecurityRepository):
        self.repository = repository

    def execute(self, name: str, expires_at: Optional[datetime] = None) -> Tuple[APIKeyEntity, str]:
        prefix  = secrets.token_hex(4) # 8 chars
        secret  = secrets.token_urlsafe(32)
        raw_key = f"kc_{prefix}.{secret}"
        
        hashed  = hashlib.sha256(raw_key.encode()).hexdigest()
        
        entity = APIKeyEntity(
            id=None,
            name=name,
            prefix=prefix,
            hashed_key=hashed,
            expires_at=expires_at
        )
        saved_entity = self.repository.save_api_key(entity)
        return saved_entity, raw_key

class VerifyAPIKeyUseCase:
    def __init__(self, repository: ISecurityRepository):
        self.repository = repository

    def execute(self, raw_key: str) -> bool:
        try:
            # Format: kc_prefix.secret
            if not raw_key.startswith("kc_") or "." not in raw_key:
                return False
            
            prefix = raw_key.split(".")[0].replace("kc_", "")
            entity = self.repository.get_api_key_by_prefix(prefix)
            
            if not entity or not entity.is_valid():
                return False
            
            # Verify hash
            hashed = hashlib.sha256(raw_key.encode()).hexdigest()
            if hashed == entity.hashed_key:
                entity.last_used = datetime.now()
                self.repository.save_api_key(entity)
                return True
            
            return False
        except Exception:
            return False
