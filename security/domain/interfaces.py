from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import APIKeyEntity
import datetime

class ISecurityRepository(ABC):
    
    @abstractmethod
    def save_api_key(self, api_key: APIKeyEntity) -> APIKeyEntity:
        pass

    @abstractmethod
    def get_api_key_by_prefix(self, prefix: str) -> Optional[APIKeyEntity]:
        pass

    @abstractmethod
    def list_all_api_keys(self) -> List[APIKeyEntity]:
        pass
