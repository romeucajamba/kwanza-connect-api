# Documentação Completa de Rotas - KwanzaConnect API (Postman)

Este documento contém **todas** as rotas atuais ativas na KwanzaConnect API, refletindo precisamente os *controllers* configurados. A aplicação base está hospedada em `http://localhost:8000/`. Todas as rotas protegidas exigem o **Token JWT** no Header `Authorization: Bearer <seu_token>` e, se configurado, o Header `X-API-KEY`.

## 1. Módulo de Autenticação e Perfis (`/api/auth/`)
> **Nota de Arquitetura:** Todas as rotas respeitantes ao Perfil do Utilizador e KYC estão neste momento mapeadas sob `/api/auth/` no sistema de roteamento (`app/urls.py`).

| Rota | Método | Descrição |
|---|---|---|
| `/api/auth/register/` | **POST** | Registar um utilizador novo |
| `/api/auth/login/` | **POST** | Autenticar utilizador e obter Tokens JWT |
| `/api/auth/logout/` | **POST** | Invalidar tokens e encerrar sessão ativa |
| `/api/auth/token/refresh/` | **POST** | Renovar Token de acesso usando Refresh Token |
| `/api/auth/verify-email/<token>/` | **GET** | Confirmar e-mail |
| `/api/auth/forgot-password/` | **POST** | Solicitar recuperação de senha (senha esquecida) |
| `/api/auth/reset-password/` | **POST** | Concluir o reset / recuperação da senha |
| `/api/auth/me/` | **GET** / **PATCH** | Obter ou editar dados do perfil do próprio utilizador |
| `/api/auth/me/change-password/` | **POST** | Alteração segura de senha com a conta logada |
| `/api/auth/users/<user_id>/` | **GET** | Ver perfil público de outro utilizador |
| `/api/auth/kyc/submit/` | **POST** | Submeter dados e documentos para KYC (`multipart/form-data`) |
| `/api/auth/kyc/status/` | **GET** | Visualizar o estado da aprovação do KYC |

## 2. Módulo de Ofertas de Câmbio (`/api/offers/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/offers/currencies/` | **GET** | Listar moedas disponíveis no sistema |
| `/api/offers/` | **GET** | Listar e pesquisar ofertas ativas (Feed Principal) |
| `/api/offers/` | **POST** | Criar nova oferta de câmbio |
| `/api/offers/mine/` | **GET** | Listar ofertas criadas por mim |
| `/api/offers/<offer_id>/` | **GET** | Detalhes de uma oferta |
| `/api/offers/<offer_id>/pause/` | **POST** | Pausar a minha oferta |
| `/api/offers/<offer_id>/resume/` | **POST** | Retomar a minha oferta pausada |
| `/api/offers/<offer_id>/close/` | **POST** | Encerrar a minha oferta definitivamente |
| `/api/offers/<offer_id>/interests/` | **GET** | Ver utilizadores que expressaram interesse na minha oferta |
| `/api/offers/<offer_id>/interest/` | **POST** | Manifestar intenção de câmbio na oferta de outro utilizador |
| `/api/offers/interests/mine/` | **GET** | Listar as propostas/interesses enviados por mim |
| `/api/offers/interests/<interest_id>/accept/` | **POST** | Aceitar propostar (Cria sala chat e bloqueia estado) |
| `/api/offers/interests/<interest_id>/reject/` | **POST** | Rejeitar a intenção de um comprador |
| `/api/offers/interests/<interest_id>/cancel/` | **POST** | Cancelar o meu próprio interesse numa oferta |

## 3. Mensagens e Chat (`/api/chat/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/chat/rooms/` | **GET** | Listar as minhas salas de conversa e últimos contactos |
| `/api/chat/rooms/<room_id>/` | **GET** | Detalhes do negócio na sala selecionada |
| `/api/chat/rooms/<room_id>/messages/` | **GET** | Histórico paginado de mensagens da sala |
| `/api/chat/rooms/<room_id>/messages/` | **POST** | Enviar mensagem para a sala |
| `/api/chat/messages/<message_id>/` | **GET** / **PUT** / **DELETE**| Gerir/Obter uma mensagem específica |

## 4. Câmbios e Estatísticas (`/api/rates/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/rates/` | **GET** | Obter tabela de taxas correntes oficiais |
| `/api/rates/convert/?from=EUR&to=AOA&amount=150`| **GET** | Conversor rápido usando parâmetros Query |
| `/api/rates/dashboard/` | **GET** | Obter estatísticas para o painel principal |

## 5. Transações (`/api/transactions/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/transactions/` | **GET** | Listar o meu histórico de transações |
| `/api/transactions/<transaction_id>/` | **GET** | Visualizar detalhe e faturas de uma transação |
| `/api/transactions/confirm/` | **POST** | Finalizar e selar um negócio (Match com Contraparte) |
| `/api/transactions/reviews/<user_id>/` | **GET** | Listar avaliações públicas de um utilizador específico |
| `/api/transactions/<transaction_id>/review/` | **POST** | Avaliar e comentar a postura da contraparte pós-negócio |

## 6. Notificações (`/api/notifications/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/notifications/` | **GET** | Listar a timeline de alertas (`?unread=true` suportado) |
| `/api/notifications/unread-count/` | **GET** | Contagem total do número de não lidas |
| `/api/notifications/mark-read/` | **POST** | Marcar globalmente todas as notificações como lidas |
| `/api/notifications/mark-read/<id>/` | **POST** | Marcar notificação especifica como lida |
| `/api/notifications/preferences/` | **GET** / **PATCH**| Consultar e atualizar preferências (Emails, Push) |

## 7. Logs de Auditoria (`/api/audit/logs/`)
*(Apenas para Utilizadores Autorizados - X-API-KEY opcional dependendo do ambiente)*

| Rota | Método | Descrição |
|---|---|---|
| `/api/audit/logs/` | **GET** | Histórico completo de auditoria para o sistema admin |
| `/api/audit/logs/<id>/` | **GET** | Consultar estado capturado (Snapshot) no instante do evento |

---

## Exemplos de Payloads (JSON)

### Auth - Registo (`POST /api/auth/register/`)
```json
{
    "email": "teste@exemplo.com",
    "password": "MinhaSenhaForte123!",
    "full_name": "João Ninguém",
    "phone": "+244923000000"
}
```

### Auth - Login (`POST /api/auth/login/`)
```json
{
    "email": "teste@exemplo.com",
    "password": "senha"
}
```

### Auth - Recuperar Senha (Forgot Password) (`POST /api/auth/forgot-password/`)
```json
{
    "email": "teste@exemplo.com"
}
```

### Auth - Concluir Recuperação (Reset Password) (`POST /api/auth/reset-password/`)
```json
{
    "token": "<token_recebido_no_email>",
    "new_password": "NovaSenhaSegura123!"
}
```

### KYC - Submissão (`POST /api/auth/kyc/submit/`) - Via Form-Data
```json
{
    "doc_type": "BI",
    "doc_number": "000000000LA000",
    "front_image": "<File>",
    "back_image": "<File>"
}
```

### Criar Oferta (`POST /api/offers/`)
```json
{
    "give_currency_code": "AOA",
    "want_currency_code": "USD",
    "give_amount": "50000.00",
    "want_amount": "50.00",
    "notes": "Entrega rápida no centro da cidade",
    "city": "Luanda"
}
```

### Aceitar Interesse (`POST /api/offers/interests/<interest_id>/accept/`)
- **Resposta**: Retorna o `room_id` da sala de chat (nova ou existente).

### Enviar Mensagem (`POST /api/chat/rooms/<room_id>/messages/`)
```json
{
    "content": "Olá, ainda tens o valor disponível?",
    "msg_type": "text",
    "reply_to": "<optional_message_id_uuid>",
    "file": null
}
```

### Manifestar Interesse (`POST /api/offers/<offer_id>/interest/`)
```json
{
    "message": "Tenho interesse, podemos fechar negócio hoje?"
}
```

### Atualizar Meu Perfil (`PATCH /api/auth/me/`)
```json
{
    "full_name": "João Silva Alterado",
    "phone": "+244900000000",
    "city": "Luanda",
    "bio": "Entusiasta de câmbios P2P",
    "is_available": true,
    "preferred_give_currency": "<uuid_aoa>",
    "preferred_want_currency": "<uuid_usd>"
}
```

### Alterar Senha (`POST /api/auth/me/change-password/`)
```json
{
    "current_password": "SenhaAtual123!",
    "new_password": "NovaSenhaSegura456!",
    "confirm_password": "NovaSenhaSegura456!"
}
```

### Avaliar Transação (`POST /api/transactions/<transaction_id>/review/`)
```json
{
    "rating": 5,
    "comment": "Negócio muito rápido e seguro. Recomendo!"
}
```

### Confirmar Transação (`POST /api/transactions/confirm/`)
```json
{
    "offer": "<id_da_oferta>",
    "room": "<id_da_sala_de_chat>"
}
```

### Atualizar Preferências Notificações (`PATCH /api/notifications/preferences/`)
```json
{
    "email_offers": true,
    "push_messages": false
}
```


