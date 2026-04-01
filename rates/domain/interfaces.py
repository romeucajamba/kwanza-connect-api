from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from decimal import Decimal
import uuid
from .entities import ConversionResultEntity, PlatformStatsEntity

class IRatesRepository(ABC):
    
    @abstractmethod
    def get_exchange_rate(self, from_code: str, to_code: str) -> Optional[Decimal]:
        pass

    @abstractmethod
    def get_platform_stats(self) -> PlatformStatsEntity:
        pass

    @abstractmethod
    def list_all_rates(self) -> List[Dict]:
        pass
