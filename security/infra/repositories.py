from typing import Optional, List
from ..models import APIKey as DjangoAPIKey
from ..domain.entities import APIKeyEntity
from ..domain.interfaces import ISecurityRepository
from django.utils import timezone

class DjangoSecurityRepository(ISecurityRepository):
    
    def _to_entity(self, django_key: DjangoAPIKey) -> APIKeyEntity:
        return APIKeyEntity(
            id=django_key.id,
            name=django_key.name,
            prefix=django_key.prefix,
            hashed_key=django_key.hashed_key,
            is_active=django_key.is_active,
            created_at=django_key.created_at,
            expires_at=django_key.expires_at,
            last_used=django_key.last_used
        )

    def save_api_key(self, api_key: APIKeyEntity) -> APIKeyEntity:
        django_key, created = DjangoAPIKey.objects.update_or_create(
            id=api_key.id,
            defaults={
                'name': api_key.name,
                'prefix': api_key.prefix,
                'hashed_key': api_key.hashed_key,
                'is_active': api_key.is_active,
                'expires_at': api_key.expires_at,
                'last_used': api_key.last_used
            }
        )
        return self._to_entity(django_key)

    def get_api_key_by_prefix(self, prefix: str) -> Optional[APIKeyEntity]:
        try:
            return self._to_entity(DjangoAPIKey.objects.get(prefix=prefix))
        except DjangoAPIKey.DoesNotExist:
            return None

    def list_all_api_keys(self) -> List[APIKeyEntity]:
        keys = DjangoAPIKey.objects.all()
        return [self._to_entity(k) for k in keys]
