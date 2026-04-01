# Guia de Rotas da API — KwanzaConnect

Este guia contém todas as rotas disponíveis na API, os métodos HTTP necessários, os corpos de requisição (JSON) e exemplos de resposta para facilitar os testes no **Postman**.

---

## 🛠️ Configuração Global (Headers)

Todas as requisições (exceto documentação) exigem os seguintes headers:

| Header | Valor | Descrição |
| :--- | :--- | :--- |
| **`Content-Type`** | `application/json` | Obrigatório para requisições com body. |
| **`X-API-KEY`** | `kc_<prefix>.<secret>` | Obrigatório para todas as rotas da API. |
| **`Authorization`** | `Bearer <seu_access_token>` | Obrigatório para rotas protegidas (após login). |

---

## 🔐 1. Autenticação (`/api/auth/`)

### Registro de Utilizador
- **Endpoint:** `POST /api/auth/register/`
- **Body:**
```json
{
  "full_name": "Romeu Cajamba",
  "email": "romeu@exemplo.com",
  "password": "senha_segura_123"
}
```
- **Resposta (201 Created):**
```json
{
  "status": "success",
  "message": "Utilizador registado com sucesso. Verifique o seu email.",
  "data": { "id": "uuid", "email": "romeu@exemplo.com" }
}
```

### Login
- **Endpoint:** `POST /api/auth/login/`
- **Body:**
```json
{
  "email": "romeu@exemplo.com",
  "password": "senha_segura_123"
}
```
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": { "id": "uuid", "full_name": "Romeu Cajamba" }
  }
}
```

### Esqueci a Senha
- **Endpoint:** `POST /api/auth/forgot-password/`
- **Body:**
```json
{
  "email": "romeu@exemplo.com"
}
```
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "message": "Instruções de recuperação enviadas para o email."
}
```

### Redefinir Senha
- **Endpoint:** `POST /api/auth/reset-password/`
- **Body:**
```json
{
  "token": "token_recebido_no_email",
  "new_password": "nova_senha_segura_123"
}
```
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "message": "Senha alterada com sucesso."
}
```

---

## 👤 2. Meu Perfil (`/api/users/me/`)

### Obter Meus Dados
- **Endpoint:** `GET /api/users/me/` (Protegida)
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "full_name": "Romeu Cajamba",
    "avatar": "url_para_imagem.jpg",
    "is_verified": true,
    ...
  }
}
```

### Atualizar Perfil (Avatar/Foto)
- **Endpoint:** `PATCH /api/users/me/` (Protegida)
- **Content-Type:** `multipart/form-data`
- **Body (Form Data):**
  - `full_name`: "Novo Nome"
  - `avatar`: [Ficheiro de Imagem]
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": { "avatar": "nova_url.jpg", ... }
}
```

### Submeter KYC (Documentos)
- **Endpoint:** `POST /api/users/kyc/` (Protegida)
- **Content-Type:** `multipart/form-data`
- **Body (Form Data):**
  - `document_type`: "id_card"
  - `document_number`: "123456789LA012"
  - `front_image`: [Ficheiro Imagem/PDF]
  - `back_image`: [Ficheiro Imagem/PDF]
- **Resposta (201 Created):**
```json
{
  "status": "success",
  "message": "Documentos submetidos para análise."
}
```

---

## 💰 3. Ofertas de Câmbio (`/api/offers/`)

### Criar Nova Oferta
- **Endpoint:** `POST /api/offers/` (Protegida)
- **Body:**
```json
{
  "give_currency_code": "AOA",
  "want_currency_code": "USD",
  "give_amount": 100000.00,
  "want_amount": 100.00,
  "offer_type": "sell",
  "expires_at": "2026-12-31T23:59:59Z"
}
```
- **Resposta (201 Created):**
```json
{
  "status": "success",
  "data": { "id": "uuid_oferta", "status": "active", ... }
}
```

### Manifestar Interesse
- **Endpoint:** `POST /api/offers/{offer_id}/interest/` (Protegida)
- **Body:** (Vazio)
- **Resposta (201 Created):**
```json
{
  "status": "success",
  "message": "Interesse registado. Uma sala de chat foi criada.",
  "data": { "id": "uuid_interesse", "room_id": "uuid_sala" }
}
```

---

## 💬 3. Chat (`/api/chat/`)

### Listar Minhas Salas
- **Endpoint:** `GET /api/chat/rooms/` (Protegida)
- **Resposta (200 OK):**
```json
{
  "count": 1,
  "results": [
    { "id": "uuid_sala", "last_message": { "content": "Olá..." }, ... }
  ]
}
```

### Enviar Mensagem
- **Endpoint:** `POST /api/chat/rooms/{room_id}/messages/` (Protegida)
- **Body:**
```json
{
  "content": "Olá, ainda tens os dólares disponíveis?",
  "msg_type": "text"
}
```

---

## 📊 4. Câmbios (`/api/rates/`)

### Conversão de Moeda
- **Endpoint:** `GET /api/rates/convert/?from=USD&to=AOA&amount=100` (Pública)
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": {
    "from_currency": "USD",
    "to_currency": "AOA",
    "amount": 100,
    "rate": 950.50,
    "converted_amount": 95050.00
  }
}
```

### Estatísticas do Dashboard
- **Endpoint:** `GET /api/rates/dashboard/` (Pública)
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": {
    "active_offers": 150,
    "total_users": 1200,
    "successful_deals": 850,
    "top_currencies": ["AOA", "USD", "EUR"]
  }
}
```

---

## 🤝 5. Transações (`/api/transactions/`)

### Confirmar Troca Concluída
- **Endpoint:** `POST /api/transactions/confirm/` (Protegida)
- **Body:**
```json
{
  "offer": "uuid_oferta",
  "room": "uuid_sala",
  "notes": "Troca feita em mãos no shopping."
}
```
- **Resposta (201 Created):**
```json
{
  "status": "success",
  "message": "Transação confirmada e registada.",
  "data": { "id": "uuid_transacao", "status": "completed" }
}
```

### Avaliar Transação
- **Endpoint:** `POST /api/transactions/{tx_id}/review/` (Protegida)
- **Body:**
```json
{
  "rating": 5,
  "comment": "Muito honesto e rápido."
}
```

---

## 🔔 6. Notificações (`/api/notifications/`)

### Listar Notificações
- **Endpoint:** `GET /api/notifications/?unread=true` (Protegida)
- **Resposta (200 OK):**
```json
{
  "results": [
    { "id": "uuid", "title": "Novo interesse", "is_read": false, ... }
  ]
}
```

### Contador de Não Lidas
- **Endpoint:** `GET /api/notifications/unread-count/` (Protegida)
- **Resposta (200 OK):**
```json
{
  "status": "success",
  "data": { "unread_count": 5 }
}
```

> [!TIP]
> Para testar os WebSockets, utilize a URL: `ws://localhost:8000/ws/chat/{room_id}/?token={seu_access_token}`.
