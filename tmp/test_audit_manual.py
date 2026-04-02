import os
import django
import uuid

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.audit_service import audit_log
from audit.infra.models import AuditLog

def test_audit():
    print("--- Testing Audit Log ---")
    action = "MANUAL_TEST"
    resource = "test_system"
    
    # Chama o helper
    result = audit_log(
        action=action,
        resource=resource,
        metadata={"info": "Running from scratch script"},
    )
    
    print(f"Audit Log ID: {result.id}")
    print(f"Action: {result.action}")
    
    # Verifica na DB
    db_log = AuditLog.objects.get(id=result.id)
    print(f"DB Record confirmed: {db_log.action}")
    print("--- Test Passed ---")

if __name__ == "__main__":
    try:
        test_audit()
    except Exception as e:
        print(f"Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
