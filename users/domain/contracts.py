"""
Contratos (interfaces) do módulo users.
Define os contratos que a camada de infra deve implementar.
"""
from abc import ABC, abstractmethod
from typing import Optional
from .entities import UserEntity


class IUserRepository(ABC):
    """Contrato para operações de persistência do utilizador."""

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        ...

    @abstractmethod
    def create(self, email: str, password: str, full_name: str, **kwargs) -> UserEntity:
        ...

    @abstractmethod
    def update(self, user_id: str, **fields) -> UserEntity:
        ...

    @abstractmethod
    def activate(self, user_id: str) -> None:
        ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        ...
