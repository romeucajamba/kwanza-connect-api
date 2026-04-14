# Documentação de Rotas - KwanzaConnect API (Postman)

Este documento contém todas as rotas ativas na KwanzaConnect API, prontas para serem importadas no Postman. A aplicação base está hospedada em `http://localhost:8000/`. Lembre-se de adicionar o **Token JWT** no Header `Authorization: Bearer <seu_token>` e, se configurado, o Header `X-API-KEY`.

## 1. Utilizadores e Autenticação (`/api/auth/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/auth/register/` | **POST** | Registar um utilizador novo |
| `/api/auth/login/` | **POST** | Autenticar utilizador e obter Tokens JWT |
| `/api/auth/token/refresh/` | **POST** | Renovar Token de acesso usando Refresh Token |
| `/api/auth/logout/` | **POST** | Invalidar tokens e encerrar sessão ativa |
| `/api/auth/verify-email/<token>/` | **GET** | Confirmar e-mail |
| `/api/auth/forgot-password/` | **POST** | Solicitar alteração de senha esquecida |
| `/api/auth/reset-password/` | **POST** | Concluir o reset da senha |
| `/api/auth/me/` | **GET** / **PUT** | Obter ou editar dados do perfil do próprio utilizador |
| `/api/auth/me/change-password/` | **POST** | Alteração segura de senha de utilizador bloqueado |
| `/api/auth/users/<user_id>/` | **GET** | Ver perfil público de outro utilizador |
| `/api/auth/kyc/submit/` | **POST** | Submeter dados e documentos para KYC |
| `/api/auth/kyc/status/` | **GET** | Visualizar o estado do KYC |

### Payloads:
**`POST /api/auth/register/`**
```json
{
    "email": "teste@exemplo.com",
    "password": "MinhaSenhaForte123!",
    "password_confirm": "MinhaSenhaForte123!",
    "full_name": "João Ninguém",
    "phone": "+244923000000",
    "country_code": "AO"
}
```

**`POST /api/auth/login/`**
```json
{
    "email": "teste@exemplo.com",
    "password": "MinhaSenhaForte123!"
}
```

**`POST /api/auth/kyc/submit/` (Multipart/form-data recomendado)**
```json
{
    "doc_type": "BI",
    "doc_number": "000000000LA000",
    "front_image": "<File>",
    "back_image": "<File>"
}
```

---

## 2. Ofertas de Câmbio (`/api/offers/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/offers/currencies/` | **GET** | Listar moedas disponíveis no sistema |
| `/api/offers/` | **GET** / **POST** | Listar ofertas ativas ou Criar Oferta |
| `/api/offers/mine/` | **GET** | Listar ofertas criadas por mim |
| `/api/offers/<offer_id>/` | **GET** | Detalhes de uma oferta |
| `/api/offers/<offer_id>/pause/` | **POST** | Pausar a minha oferta |
| `/api/offers/<offer_id>/resume/` | **POST** | Retomar a minha oferta |
| `/api/offers/<offer_id>/close/` | **POST** | Encerrar a minha oferta definitivamente |
| `/api/offers/<offer_id>/interests/` | **GET** | Listar utilizadores interessados nesta oferta |
| `/api/offers/<offer_id>/interest/` | **POST** | Demonstrar intenção de câmbio (como comprador) |
| `/api/offers/interests/mine/` | **GET** | Listar propostas/interesses submetidos por mim |
| `/api/offers/interests/<interest_id>/accept/` | **POST** | Aceitar a intenção de um comprador (Cria sala chat) |
| `/api/offers/interests/<interest_id>/reject/` | **POST** | Rejeitar a intenção de um comprador |

### Payloads:
**`POST /api/offers/`**
```json
{
    "give_currency_id": "<uuid_kwanza>",
    "give_amount": "50000.00",
    "want_currency_id": "<uuid_euro>",
    "want_amount": "50.00"
}
```

**`POST /api/offers/<offer_id>/interest/`**
```json
{
    "notes": "Tenho o valor exato, podemos fazer agora."
}
```

---

## 3. Mensagens e Chat (`/api/chat/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/chat/rooms/` | **GET** | Listar as minhas salas de conversa |
| `/api/chat/rooms/<room_id>/` | **GET** | Detalhe da sala e informações do outro utilizador |
| `/api/chat/rooms/<room_id>/messages/` | **GET** / **POST** | Listar mensagens ou Enviar mensagem |
| `/api/chat/messages/<message_id>/` | **PUT** / **DELETE**| Editar ou apagar uma mensagem (soft delete) |

### Payloads:
**`POST /api/chat/rooms/<room_id>/messages/`**
```json
{
    "content": "Olá, queres efetuar a transferência já?",
    "msg_type": "text"
}
```

---

## 4. Transações (`/api/transactions/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/transactions/` | **GET** | Listar transações ocorridas |
| `/api/transactions/<transaction_id>/` | **GET** | Detalhes e Status da transacção |
| `/api/transactions/confirm/` | **POST** | Pressionar botão de selar o acordo (Match e Fecho de Oferta) |
| `/api/transactions/<transaction_id>/review/` | **POST** | Avaliar e adicionar review após negócio concluído |

### Payloads:
**`POST /api/transactions/confirm/`**
```json
{
    "offer_id": "<uuid_da_oferta>",
    "room_id": "<uuid_da_sala_de_chat>"
}
```

**`POST /api/transactions/<transaction_id>/review/`**
```json
{
    "rating": 5,
    "comment": "Foi rápido e eficiente!"
}
```

---

## 5. Taxas de Câmbio (`/api/rates/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/rates/` | **GET** | Obter tabela de taxas de câmbios em tempo real via Open Exchange Rates |
| `/api/rates/convert/` | **POST** | Converter rapidamente entre duas moedas baseando na taxa |
| `/api/rates/dashboard/` | **GET** | Status Geral da Plataforma (Usuários Ativos, Total Volume Negociado) |

### Payloads:
**`POST /api/rates/convert/`**
```json
{
    "source_currency": "EUR",
    "target_currency": "AOA",
    "amount": "150.00"
}
```

---

## 6. Notificações (`/api/notifications/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/notifications/` | **GET** | Obter de notificações para o painel de alerta |
| `/api/notifications/unread-count/` | **GET** | Número total de não lidas |
| `/api/notifications/mark-read/` | **POST** | Marcar todas como lidas |
| `/api/notifications/mark-read/<id>/` | **POST** | Marcar uma notificação específica como lida |
| `/api/notifications/preferences/` | **GET** / **PUT**|  Gerir Push e E-mail de notificação |

### Payloads:
**`PUT /api/notifications/preferences/`**
```json
{
    "email_offers": true,
    "push_messages": true
}
```

---

## 7. Registos de Auditoria (`/api/audit/logs/`)
Esta rota é acessível apenas a utilizadores **Superadmin** (via painel superuser).

| Rota | Método | Descrição |
|---|---|---|
| `/api/audit/logs/` | **GET** | Filtrar Log/Registo auditório paginado. Aceita filtro `?action=X` |
| `/api/audit/logs/<id>/` | **GET** | Exibir todo o snapshot do log submetido |
