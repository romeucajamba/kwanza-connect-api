# KwanzaConnect API — Plataforma de Câmbio P2P

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean--Architecture-blue)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 📝 Sobre o Software
A **KwanzaConnect API** é uma solução robusta para facilitar a troca de moedas entre indivíduos (Peer-to-Peer). A plataforma permite que utilizadores publiquem propostas de câmbio, encontrem parceiros de negócio em tempo real, negociem via chat integrado e acompanhem as taxas de câmbio mundiais atualizadas.

**Propósito:** Democratizar o acesso ao câmbio, permitindo que as pessoas negociem valores de forma direta, segura e transparente, sem a necessidade de intermediários bancários complexos para pequenas operações.

---

## 👤 Criador
Este projeto foi idealizado e desenvolvido por **Romeu Cajamba**.

---

## 🛠️ Tecnologias Utilizadas
- **Backend:** Python 3.10+ & Django 4.2+
- **API Framework:** Django REST Framework (DRF)
- **Real-Time:** Django Channels (WebSockets) com Redis Layer
- **Email Service:** Mock Terminal (Dev) / SMTP (Prod)
- **Base de Dados:** PostgreSQL
- **Cache & Message Broker:** Redis
- **Tarefas de Fundo:** Celery & Celery Beat
- **Documentação:** DRF Spectacular (OpenAPI 3 / Swagger)
- **Segurança:** SimpleJWT (JSON Web Tokens), Argon2 & API Key Auth
- **Ambiente:** Docker & Docker Compose

---

## 🏛️ Arquitetura e Organização
O projeto foi totalmente refatorado seguindo os princípios de **Clean Architecture**, **SOLID** e **Clean Code**. Esta abordagem desacopla a lógica de negócio do framework (Django), facilitando a manutenção e a testabilidade.

### Estrutura de Pastas (por Módulo)
Cada módulo (`users`, `offers`, `chat`, `notifications`, `rates`, `transactions`, `security`) segue rigorosamente este padrão:

1. **`domain/` (Coração do Sistema)**:
   - `entities.py`: Classes Python puras (POPOs) que representam os conceitos reais.
   - `interfaces.py`: Contratos abstratos (ABCs) para Repositórios e Serviços.
2. **`services/` (Casos de Uso)**:
   - `use_cases.py`: Orquestram a lógica da aplicação operando apenas sobre Entidades e Interfaces (DI via construtor).
3. **`infra/` (Detalhes Técnicos)**:
   - `repositories.py`: Implementações dos contratos usando o ORM do Django.
   - `serializers.py`: Transformação de dados para a API (DRF).
   - `services.py`: Adaptadores de infraestrutura para comunicação entre módulos.
4. **`controllers/` (Interface de Entrada)**:
   - `views.py`: Views do Django que injetam os repositórios concretos nos Casos de Uso.
5. **`tests/` (Garantia de Qualidade)**:
   - `unit/`: Testes de lógica de negócio usando Mocks para isolamento total.
   - `e2e/`: Testes de ponta a ponta que validam o fluxo completo da API.

---

## 🧪 Testes e Qualidade
A API conta com uma suíte de testes automatizados utilizando `pytest` e `pytest-django`.

**Executar todos os testes:**
```bash
# Ativar o ambiente virtual
.\venv\Scripts\activate

# Executar a suíte completa
pytest
```

**Módulos Cobertos:**
A refatoração incluiu a criação de testes para todos os módulos críticos: `users`, `offers`, `chat`, `notifications`, `rates`, `transactions` e `security`.

---

## ⚖️ Regras de Negócio
1. **Verificação (KYC):** Apenas utilizadores com documentos aprovados podem publicar ofertas ou aceitar interesses (configurável via permissões).
2. **Ciclo de Oferta:** Uma oferta pode estar `Ativa`, `Pausada`, `Expirada` ou `Encerrada`.
3. **Interesses:** Quando um utilizador demonstra interesse, uma sala de chat privada é criada entre as partes.
4. **Taxas Reais:** O sistema atualiza as taxas de câmbio mundiais a cada 5 minutos via Celery Beat para servir de referência.
5. **Avaliação:** Após a conclusão de uma transação, ambos os participantes podem avaliar-se mutuamente (1 a 5 estrelas).
6. **Recuperação de Conta:** Fluxo completo de "Esqueci a Senha" com tokens seguros e expiração de 2 horas.
7. **Tempo Real:** Notificações e mensagens de chat são entregues via WebSockets instantaneamente.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Docker e Docker Compose instalados.
- Ficheiro `.env` configurado (ver `exemple.env`).

### Execução via Docker (Recomendado)
```bash
# 1. Construir e subir os containers
docker compose up --build -d

# 2. Correr as migrações da base de dados
docker compose exec web python manage.py migrate

# 3. Criar um administrador
docker compose exec web python manage.py createsuperuser

# 4. Verificar os logs
docker compose logs -f web
```

### Execução Local (Desenvolvimento)
Se preferir rodar sem Docker, precisará do PostgreSQL e Redis ativos:
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar migrações
python manage.py migrate

# 3. Iniciar o servidor de desenvolvimento
python manage.py runserver

# 4. Iniciar o Worker do Celery (em outro terminal)
celery -A app worker -l info
```

---

## 🧪 Como Testar no Postman
1. **Documentação Swagger:** Aceda a `http://localhost:8000/api/docs/` para ver todos os endpoints disponíveis.
2. **Segurança (Obrigatório):**
   - Todas as requisições à API agora exigem o header **`X-API-KEY`**.
   - Podes gerar uma chave no Painel Administrativo (`/admin/security/apikey/`).
   - No Postman, adiciona o Header: `X-API-KEY: kc_<prefix>.<secret>`.
3. **Autenticação:**
   - Faça POST em `/api/auth/register/` (com `X-API-KEY`) para criar conta.
   - Faça POST em `/api/auth/login/` para obter os tokens `access` e `refresh`.
   - No Postman, use o `access` token no Header como `Authorization: Bearer <seu_token>`.
3. **Módulos:**
   - **Ofertas:** GET `/api/offers/` para ver propostas.
   - **Chat (WS):** Use a URL `ws://localhost:8000/ws/chat/<room_id>/` para testar WebSockets.

---

## 📜 Licença
Este software é propriedade privada de **Romeu Cajamba**.