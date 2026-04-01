"""
Repositório concreto do módulo users.
Implementa IUserRepository usando os modelos Django.
"""
from typing import Optional
from django.utils import timezone
from ..domain.contracts import IUserRepository
from ..domain.entities import UserEntity
from ..models import User


class UserRepository(IUserRepository):

    def _to_entity(self, user: User) -> UserEntity:
        return UserEntity(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            country_code=user.country_code,
            city=user.city,
            bio=user.bio,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_available=user.is_available,
            verification_status=user.verification_status,
            preferred_give_currency=user.preferred_give_currency,
            preferred_want_currency=user.preferred_want_currency,
            date_joined=user.date_joined,
            last_seen=user.last_seen,
            avatar_url=user.avatar.url if user.avatar else None,
        )

    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        try:
            return self._to_entity(User.objects.get(id=user_id))
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            return self._to_entity(User.objects.get(email=email))
        except User.DoesNotExist:
            return None

    def create(self, email: str, password: str, full_name: str, **kwargs) -> UserEntity:
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            **kwargs,
        )
        return self._to_entity(user)

    def update(self, user_id: str, **fields) -> UserEntity:
        User.objects.filter(id=user_id).update(**fields)
        return self.get_by_id(user_id)

    def activate(self, user_id: str) -> None:
        User.objects.filter(id=user_id).update(is_active=True)

    def exists_by_email(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()
