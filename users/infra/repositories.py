from typing import Optional, List
import uuid
from django.db import transaction
from django.utils import timezone
from .models import User as DjangoUser, UserSecurity as DjangoUserSecurity, IdentityDocument as DjangoIdentityDocument
from ..domain.entities import UserEntity, UserSecurityEntity, IdentityDocumentEntity
from ..domain.interfaces import IUserRepository

class DjangoUserRepository(IUserRepository):
    
    def _to_entity(self, django_user: DjangoUser) -> UserEntity:
        security = None
        if hasattr(django_user, 'security'):
            security = self._security_to_entity(django_user.security)
            
        identity_document = None
        if hasattr(django_user, 'identity_document'):
            identity_document = self._identity_to_entity(django_user.identity_document)
            
        return UserEntity(
            id=django_user.id,
            email=django_user.email,
            full_name=django_user.full_name,
            is_active=django_user.is_active,
            is_staff=django_user.is_staff,
            is_verified=django_user.is_verified,
            is_available=django_user.is_available,
            verification_status=django_user.verification_status,
            phone=django_user.phone,
            country_code=django_user.country_code,
            city=django_user.city,
            address=django_user.address,
            occupation=django_user.occupation,
            bio=django_user.bio,
            avatar=django_user.avatar.url if django_user.avatar else None,
            last_seen=django_user.last_seen,
            date_joined=django_user.date_joined,
            preferred_give_currency=django_user.preferred_give_currency,
            preferred_want_currency=django_user.preferred_want_currency,
            security=security,
            identity_document=identity_document
        )

    def _security_to_entity(self, django_security: DjangoUserSecurity) -> UserSecurityEntity:
        return UserSecurityEntity(
            id=django_security.id,
            user_id=django_security.user_id,
            email_token=django_security.email_token,
            email_verified=django_security.email_verified,
            email_verified_at=django_security.email_verified_at,
            phone_otp=django_security.phone_otp,
            phone_otp_expires_at=django_security.phone_otp_expires_at,
            phone_verified=django_security.phone_verified,
            failed_login_attempts=django_security.failed_login_attempts,
            locked_until=django_security.locked_until,
            two_factor_enabled=django_security.two_factor_enabled,
            two_factor_secret=django_security.two_factor_secret,
            password_changed_at=django_security.password_changed_at,
            password_reset_token=django_security.password_reset_token,
            password_reset_expires=django_security.password_reset_expires
        )

    def _identity_to_entity(self, django_identity: DjangoIdentityDocument) -> IdentityDocumentEntity:
        return IdentityDocumentEntity(
            id=django_identity.id,
            user_id=django_identity.user_id,
            doc_type=django_identity.doc_type,
            doc_number=django_identity.doc_number,
            doc_country=django_identity.doc_country,
            status=django_identity.status,
            front_image=django_identity.front_image.url if django_identity.front_image else None,
            back_image=django_identity.back_image.url if django_identity.back_image else None,
            pdf_file=django_identity.pdf_file.url if django_identity.pdf_file else None,
            rejection_reason=django_identity.rejection_reason,
            submitted_at=django_identity.submitted_at,
            reviewed_at=django_identity.reviewed_at,
            reviewed_by_id=django_identity.reviewed_by_id
        )

    def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            return self._to_entity(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            django_user = DjangoUser.objects.get(email=email)
            return self._to_entity(django_user)
        except DjangoUser.DoesNotExist:
            return None

    def exists_by_email(self, email: str) -> bool:
        return DjangoUser.objects.filter(email=email).exists()

    def save(self, user_entity: UserEntity) -> UserEntity:
        with transaction.atomic():
            django_user, created = DjangoUser.objects.update_or_create(
                id=user_entity.id,
                defaults={
                    'email': user_entity.email,
                    'full_name': user_entity.full_name,
                    'is_active': user_entity.is_active,
                    'is_staff': user_entity.is_staff,
                    'is_verified': user_entity.is_verified,
                    'is_available': user_entity.is_available,
                    'verification_status': user_entity.verification_status,
                    'phone': user_entity.phone,
                    'country_code': user_entity.country_code,
                    'city': user_entity.city,
                    'address': user_entity.address,
                    'occupation': user_entity.occupation,
                    'bio': user_entity.bio,
                    'last_seen': user_entity.last_seen,
                    'preferred_give_currency': user_entity.preferred_give_currency,
                    'preferred_want_currency': user_entity.preferred_want_currency,
                }
            )
            # Se for novo ou atualizado, podemos precisar lidar com senha separadamente se for o caso
            # mas o save de entidade não deve lidar com senhas diretamente se existirem usecases para isso.
            
            if user_entity.security:
                self.update_security(user_entity.security)
                
            return self._to_entity(django_user)

    def update_security(self, security: UserSecurityEntity) -> None:
        DjangoUserSecurity.objects.update_or_create(
            id=security.id,
            defaults={
                'user_id': security.user_id,
                'email_token': security.email_token,
                'email_verified': security.email_verified,
                'email_verified_at': security.email_verified_at,
                'phone_otp': security.phone_otp,
                'phone_otp_expires_at': security.phone_otp_expires_at,
                'phone_verified': security.phone_verified,
                'failed_login_attempts': security.failed_login_attempts,
                'locked_until': security.locked_until,
                'two_factor_enabled': security.two_factor_enabled,
                'two_factor_secret': security.two_factor_secret,
                'password_changed_at': security.password_changed_at,
                'password_reset_token': security.password_reset_token,
                'password_reset_expires': security.password_reset_expires,
            }
        )

    def get_security_by_user_id(self, user_id: uuid.UUID) -> Optional[UserSecurityEntity]:
        try:
            django_security = DjangoUserSecurity.objects.get(user_id=user_id)
            return self._security_to_entity(django_security)
        except DjangoUserSecurity.DoesNotExist:
            return None

    def get_security_by_email_token(self, token: str) -> Optional[UserSecurityEntity]:
        try:
            django_security = DjangoUserSecurity.objects.get(email_token=token)
            return self._security_to_entity(django_security)
        except DjangoUserSecurity.DoesNotExist:
            return None

    def get_security_by_reset_token(self, token: str) -> Optional[UserSecurityEntity]:
        try:
            django_security = DjangoUserSecurity.objects.get(password_reset_token=token)
            return self._security_to_entity(django_security)
        except DjangoUserSecurity.DoesNotExist:
            return None

    def save_kyc_document(self, document: IdentityDocumentEntity) -> None:
        DjangoIdentityDocument.objects.update_or_create(
            id=document.id,
            defaults={
                'user_id': document.user_id,
                'doc_type': document.doc_type,
                'doc_number': document.doc_number,
                'doc_country': document.doc_country,
                'status': document.status,
                'rejection_reason': document.rejection_reason,
                'reviewed_at': document.reviewed_at,
                'reviewed_by_id': document.reviewed_by_id,
            }
        )

    def get_kyc_document_by_user_id(self, user_id: uuid.UUID) -> Optional[IdentityDocumentEntity]:
        try:
            django_identity = DjangoIdentityDocument.objects.get(user_id=user_id)
            return self._identity_to_entity(django_identity)
        except DjangoIdentityDocument.DoesNotExist:
            return None
