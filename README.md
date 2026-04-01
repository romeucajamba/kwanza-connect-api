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
- **Real-Time:** Django Channels (WebSockets)
- **Base de Dados:** PostgreSQL
- **Cache & Message Broker:** Redis
- **Tarefas de Fundo:** Celery & Celery Beat
- **Documentação:** DRF Spectacular (OpenAPI 3 / Swagger)
- **Segurança:** SimpleJWT (JSON Web Tokens)
- **Ambiente:** Docker & Docker Compose

---

## 🏛️ Arquitetura e Organização
O projeto foi refatorado seguindo os princípios de **Clean Architecture** e **SOLID**, garantindo que a lógica de negócio seja independente de frameworks e fácil de testar.

### Estrutura de Pastas (por Módulo)
Cada módulo (`users`, `offers`, `chat`, etc.) segue este padrão:
- `domain/`: Entidades puras e Interfaces/Contratos.
- `services/`: Casos de Uso (logic of the application).
- `infra/`: Implementações técnicas (Repositórios, Serializers, Providers).
- `controllers/`: Camada de entrada (Django Views).
- `routes/`: Definições de URLs.

**Módulos Principais:**
- **Users:** Gestão de utilizadores, Autenticação JWT e Verificação de Identidade (KYC).
- **Offers:** Publicação e gestão de propostas de câmbio.
- **Chat:** Comunicação em tempo real entre interessados.
- **Notifications:** Sistema de alertas multicanal (WebSocket, Push, Email).
- **Rates:** Integração com APIs de câmbio externo e estatísticas.
- **Transactions:** Histórico de trocas concluídas e sistema de avaliações (Ratings).

---

## ⚖️ Regras de Negócio
1. **Verificação (KYC):** Apenas utilizadores com documentos aprovados podem publicar ofertas ou aceitar interesses (configurável via permissões).
2. **Ciclo de Oferta:** Uma oferta pode estar `Ativa`, `Pausada`, `Expirada` ou `Encerrada`.
3. **Interesses:** Quando um utilizador demonstra interesse, uma sala de chat privada é criada entre as partes.
4. **Taxas Reais:** O sistema atualiza as taxas de câmbio mundiais a cada 5 minutos via Celery Beat para servir de referência.
5. **Avaliação:** Após a conclusão de uma transação, ambos os participantes podem avaliar-se mutuamente (1 a 5 estrelas).

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