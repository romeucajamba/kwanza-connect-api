import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from security.infra.repositories import DjangoSecurityRepository
from security.services.use_cases import GenerateAPIKeyUseCase

def generate_key():
    repo = DjangoSecurityRepository()
    use_case = GenerateAPIKeyUseCase(repo)
    
    name = "Chave de Desenvolvimento Frontend"
    key_entity, raw_key = use_case.execute(name)
    
    print(f"\n✅ Chave de API gerada com sucesso!")
    print(f"Nome: {key_entity.name}")
    print(f"Prefixo: {key_entity.prefix}")
    print(f"Valor (Header X-API-KEY): {raw_key}")
    print(f"\n⚠️ Guarde esta chave! Ela será usada no .env do seu frontend como VITE_X_API_KEY.\n")

if __name__ == "__main__":
    generate_key()
