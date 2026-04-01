"""Contrato para providers de taxa de câmbio externa."""
from abc import ABC, abstractmethod
from typing import Dict


class IRateProvider(ABC):
    """Interface para qualquer fonte de taxas de câmbio."""

    @abstractmethod
    def fetch(self, base_currency: str) -> Dict[str, float]:
        """
        Busca taxas de câmbio para uma moeda base.
        Retorna: {'USD': 1.0, 'EUR': 0.92, 'AOA': 850.0, ...}
        """
        ...
