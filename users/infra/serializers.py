"""
Serializers do módulo users.
Validação de dados de entrada — nenhuma informação sensível é exposta nas saídas.
"""
from rest_framework import serializers
from ..models import User, IdentityDocument


# ─────────────────────────────────────────────
#  Registo e autenticação
# ─────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model  = User
        fields = ['email', 'full_name', 'phone', 'country_code', 'password', 'password_confirm']
        extra_kwargs = {
            'email':        {'required': True},
            'full_name':    {'required': True},
            'phone':        {'required': False},
            'country_code': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Este email já está registado.')
        return value.lower()

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas não coincidem.'})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password     = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'As senhas não coincidem.'})
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token            = serializers.CharField()
    new_password     = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'As senhas não coincidem.'})
        return data


# ─────────────────────────────────────────────
#  Perfil público (sem dados sensíveis)
# ─────────────────────────────────────────────

class PublicUserSerializer(serializers.ModelSerializer):
    """Perfil público — exposto a outros utilizadores."""
    class Meta:
        model  = User
        fields = [
            'id', 'full_name', 'country_code', 'city',
            'bio', 'avatar', 'is_available', 'is_verified',
            'preferred_give_currency', 'preferred_want_currency',
            'date_joined',
        ]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """Perfil completo — apenas para o próprio utilizador."""
    class Meta:
        model  = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'country_code',
            'city', 'address', 'occupation', 'bio', 'avatar',
            'is_active', 'is_verified', 'is_available',
            'verification_status', 'preferred_give_currency',
            'preferred_want_currency', 'last_seen', 'date_joined',
        ]
        read_only_fields = [
            'id', 'email', 'is_active', 'is_verified',
            'verification_status', 'last_seen', 'date_joined',
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'full_name', 'phone', 'city', 'address',
            'occupation', 'bio', 'avatar',
            'preferred_give_currency', 'preferred_want_currency',
            'is_available',
        ]


# ─────────────────────────────────────────────
#  KYC — Documentos de identidade
# ─────────────────────────────────────────────

class IdentityDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = IdentityDocument
        fields = [
            'id', 'doc_type', 'doc_number', 'doc_country',
            'front_image', 'back_image', 'pdf_file',
            'status', 'rejection_reason', 'submitted_at',
        ]
        read_only_fields = ['id', 'status', 'rejection_reason', 'submitted_at']

    def validate(self, data):
        has_images = data.get('front_image') and data.get('back_image')
        has_pdf    = bool(data.get('pdf_file'))
        if not has_images and not has_pdf:
            raise serializers.ValidationError(
                'Envie frente + verso do documento OU um ficheiro PDF.'
            )
        return data
