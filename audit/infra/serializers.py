from rest_framework import serializers
from .models import AuditLog
from users.infra.serializers import PublicUserSerializer

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'resource', 
            'resource_id', 'metadata', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields
