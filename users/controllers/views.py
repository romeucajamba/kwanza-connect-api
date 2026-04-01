"""
Controllers (Views) do módulo users.
Responsabilidade única: HTTP ↔ Use Cases.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
import uuid

from app.exceptions import success_response, created_response
from app.permissions import IsSelf
from ..infra.serializers import (
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    UserProfileSerializer, UpdateProfileSerializer, IdentityDocumentSerializer,
    PublicUserSerializer,
)
from ..services.use_cases import (
    RegisterUserUseCase, LoginUseCase, VerifyEmailUseCase,
    ChangePasswordUseCase, ForgotPasswordUseCase, ResetPasswordUseCase,
    UpdateProfileUseCase, SubmitKYCUseCase,
)
from ..infra.repositories import DjangoUserRepository
from ..infra.email_service import TerminalEmailService
from ..models import User


# ─────────────────────────────────────────────
#  Autenticação
# ─────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, tags=['Autenticação'])
    def post(self, request):
        repo = DjangoUserRepository()
        email_service = TerminalEmailService()
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = RegisterUserUseCase(repo, email_service).execute(**serializer.validated_data)
        return created_response(data=result, message='Conta criada com sucesso. Verifique o seu email.')


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, tags=['Autenticação'])
    def post(self, request):
        repo = DjangoUserRepository()
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = LoginUseCase(repo).execute(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        return success_response(data=tokens, message='Login realizado com sucesso.')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Autenticação'])
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'refresh': 'O token de refresh é obrigatório.'})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass  # token já inválido — não expor detalhes
        return success_response(message='Sessão terminada com sucesso.')


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['Autenticação'])
    def get(self, request, token: str):
        repo = DjangoUserRepository()
        VerifyEmailUseCase(repo).execute(token=token)
        return success_response(message='Email verificado com sucesso. Já pode fazer login.')


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=ForgotPasswordSerializer, tags=['Autenticação'])
    def post(self, request):
        repo = DjangoUserRepository()
        email_service = TerminalEmailService()
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ForgotPasswordUseCase(repo, email_service).execute(email=serializer.validated_data['email'])
        return success_response(
            message='Se o email existir na plataforma, receberá um link de reset em breve.'
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=ResetPasswordSerializer, tags=['Autenticação'])
    def post(self, request):
        repo = DjangoUserRepository()
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ResetPasswordUseCase(repo).execute(
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password'],
        )
        return success_response(message='Senha alterada com sucesso. Já pode fazer login.')


# ─────────────────────────────────────────────
#  Perfil
# ─────────────────────────────────────────────

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(tags=['Perfil'])
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)

    @extend_schema(request=UpdateProfileSerializer, tags=['Perfil'])
    def patch(self, request):
        repo = DjangoUserRepository()
        # O serializer valida os dados, incluindo arquivos se presentes
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Executa o Use Case com os campos validados (que podem conter InMemoryUploadedFile)
        updated_user = UpdateProfileUseCase(repo).execute(
            user_id=request.user.id, 
            **serializer.validated_data
        )
        
        return success_response(
            data=UserProfileSerializer(updated_user).data,
            message='Perfil actualizado com sucesso.'
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, tags=['Perfil'])
    def post(self, request):
        repo = DjangoUserRepository()
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ChangePasswordUseCase(repo).execute(
            user_id=request.user.id,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password'],
        )
        return success_response(message='Senha alterada com sucesso.')


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Perfil'])
    def get(self, request, user_id: str):
        repo = DjangoUserRepository()
        user_entity = repo.get_by_id(uuid.UUID(user_id))
        if not user_entity or not user_entity.is_active:
            from rest_framework.exceptions import NotFound
            raise NotFound('Utilizador não encontrado.')
        
        # O Serializer do DRF ainda espera um Model ou um objeto com os mesmos atributos.
        # Como as nossas entidades têm os mesmos nomes de atributos, deve funcionar.
        serializer = PublicUserSerializer(user_entity)
        return success_response(data=serializer.data)


# ─────────────────────────────────────────────
#  KYC
# ─────────────────────────────────────────────

class KYCSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    @extend_schema(request=IdentityDocumentSerializer, tags=['KYC'])
    def post(self, request):
        repo = DjangoUserRepository()
        serializer = IdentityDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        SubmitKYCUseCase(repo).execute(user_id=request.user.id, doc_data=serializer.validated_data)
        return success_response(message='Documentos enviados. A análise demora até 48 horas.')


class KYCStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['KYC'])
    def get(self, request):
        data = {
            'verification_status': request.user.verification_status,
            'is_verified':         request.user.is_verified,
        }
        if hasattr(request.user, 'identity_document'):
            doc = request.user.identity_document
            data['document'] = {
                'status':           doc.status,
                'rejection_reason': doc.rejection_reason or None,
                'submitted_at':     doc.submitted_at,
            }
        return success_response(data=data)
