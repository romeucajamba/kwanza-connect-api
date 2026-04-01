"""
Use cases do módulo users.
Orquestra repositórios e lógica de negócio sem conhecer Django ou HTTP.
"""
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound, PermissionDenied

from ..models import User, UserSecurity


def _get_token_pair(user: User) -> dict:
    """Gera par de tokens JWT para o utilizador."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


class RegisterUserUseCase:
    def execute(self, email: str, password: str, full_name: str, **kwargs) -> dict:
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Este email já está registado.'})

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            **kwargs,
        )

        # Gera token de verificação de email
        security = user.security
        token    = secrets.token_urlsafe(32)
        security.email_token = hashlib.sha256(token.encode()).hexdigest()
        security.save(update_fields=['email_token'])

        # TODO: enviar email com link de verificação contendo o token raw
        # SendEmailUseCase.send_verification(user, token)

        return {
            'id':       str(user.id),
            'email':    user.email,
            'message':  'Conta criada. Verifique o seu email para activar a conta.',
        }


class LoginUseCase:
    def execute(self, email: str, password: str) -> dict:
        try:
            user     = User.objects.select_related('security').get(email=email)
            security = user.security
        except User.DoesNotExist:
            raise AuthenticationFailed('Credenciais inválidas.')

        if security.is_locked:
            raise AuthenticationFailed(
                'Conta bloqueada por excesso de tentativas. Tente novamente em 15 minutos.'
            )

        if not user.is_active:
            raise AuthenticationFailed('Conta não activada. Verifique o seu email.')

        authenticated = authenticate(username=email, password=password)
        if not authenticated:
            security.register_failed_login()
            attempts_left = max(0, 5 - security.failed_login_attempts)
            msg = f'Credenciais inválidas.'
            if attempts_left > 0:
                msg += f' Tentativas restantes: {attempts_left}.'
            raise AuthenticationFailed(msg)

        security.reset_failed_logins()
        user.update_last_seen()

        return _get_token_pair(user)


class VerifyEmailUseCase:
    def execute(self, token: str) -> None:
        hashed = hashlib.sha256(token.encode()).hexdigest()
        try:
            security = UserSecurity.objects.select_related('user').get(email_token=hashed)
        except UserSecurity.DoesNotExist:
            raise ValidationError('Token de verificação inválido ou já utilizado.')

        if security.email_verified:
            raise ValidationError('O email já foi verificado.')

        security.email_verified    = True
        security.email_token       = ''
        security.email_verified_at = timezone.now()
        security.save(update_fields=['email_verified', 'email_token', 'email_verified_at'])

        user           = security.user
        user.is_active = True
        user.save(update_fields=['is_active'])


class ChangePasswordUseCase:
    def execute(self, user: User, current_password: str, new_password: str) -> None:
        if not user.check_password(current_password):
            raise ValidationError({'current_password': 'Senha actual incorrecta.'})
        if current_password == new_password:
            raise ValidationError({'new_password': 'A nova senha deve ser diferente da actual.'})
        user.set_password(new_password)
        user.save(update_fields=['password'])

        security = user.security
        security.password_changed_at = timezone.now()
        security.save(update_fields=['password_changed_at'])


class ForgotPasswordUseCase:
    def execute(self, email: str) -> None:
        """
        Gera token de reset.
        Não confirma se o email existe para evitar enumeração de utilizadores.
        """
        try:
            user     = User.objects.select_related('security').get(email=email, is_active=True)
            security = user.security
        except User.DoesNotExist:
            return  # resposta silenciosa — não expõe se o email existe

        token    = secrets.token_urlsafe(32)
        hashed   = hashlib.sha256(token.encode()).hexdigest()
        security.password_reset_token   = hashed
        security.password_reset_expires = timezone.now() + timedelta(hours=1)
        security.save(update_fields=['password_reset_token', 'password_reset_expires'])

        # TODO: enviar email com link contendo o token raw
        # SendEmailUseCase.send_reset(user, token)


class ResetPasswordUseCase:
    def execute(self, token: str, new_password: str) -> None:
        hashed = hashlib.sha256(token.encode()).hexdigest()
        try:
            security = UserSecurity.objects.select_related('user').get(
                password_reset_token=hashed
            )
        except UserSecurity.DoesNotExist:
            raise ValidationError('Token inválido ou já utilizado.')

        if security.password_reset_expires < timezone.now():
            raise ValidationError('O link de reset expirou. Solicite um novo.')

        user = security.user
        user.set_password(new_password)
        user.save(update_fields=['password'])

        security.password_reset_token   = ''
        security.password_reset_expires = None
        security.password_changed_at    = timezone.now()
        security.save(update_fields=['password_reset_token', 'password_reset_expires', 'password_changed_at'])


class UpdateProfileUseCase:
    def execute(self, user: User, **fields) -> User:
        allowed = {
            'full_name', 'phone', 'city', 'address', 'occupation',
            'bio', 'avatar', 'preferred_give_currency',
            'preferred_want_currency', 'is_available',
        }
        update = {k: v for k, v in fields.items() if k in allowed}
        for attr, val in update.items():
            setattr(user, attr, val)
        user.save(update_fields=list(update.keys()))
        return user


class SubmitKYCUseCase:
    def execute(self, user: User, doc_data: dict) -> None:
        from ..models import IdentityDocument
        if hasattr(user, 'identity_document') and user.identity_document.status == 'approved':
            raise ValidationError('Os documentos já foram aprovados.')

        IdentityDocument.objects.update_or_create(
            user=user,
            defaults=doc_data,
        )
        user.verification_status = 'submitted'
        user.save(update_fields=['verification_status'])
