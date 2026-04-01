# Guia de Configuração Docker — KwanzaConnect API

Este documento explica o propósito e a função dos arquivos de configuração localizados na pasta `docker/`, que garantem que o ambiente de execução da aplicação seja consistente, seguro e escalável.

---

## 📂 Estrutura de Arquivos

### 1. `docker/entrypoint.sh`
Este script é o **ponto de entrada** do container da aplicação Django. Ele é executado automaticamente sempre que o serviço `web` (ou `celery`) inicia.

**Principais Funções:**
- **Health Check de Serviços**: Utiliza o utilitário `nc` (netcat) para verificar se o banco de dados PostgreSQL e o Redis já estão aceitando conexões antes de prosseguir.
- **Gestão de Esquemas**: Executa `python manage.py migrate` para sincronizar as tabelas do banco de dados com os modelos da aplicação.
- **Preparação de Ativos**: Utiliza `collectstatic` para reunir todos os arquivos estáticos (CSS, JS, Imagens) em um diretório centralizado para o Nginx.
- **Automação de Admin**: Tenta criar um **Superuser** inicial baseado nas variáveis de ambiente (`DJANGO_SUPERUSER_EMAIL` e `PASSWORD`), garantindo que o painel administrativo esteja pronto após o primeiro `up`.
- **Handoff de Comando**: No final, utiliza `exec "$@"` para rodar o comando final definido no `docker-compose.yml` (por exemplo, iniciar o Gunicorn ou Celery).

---

### 2. `docker/nginx/nginx.conf`
O **Nginx** atua como um **Proxy Reverso** e Servidor de Arquivos Estáticos. Ele senta-se na frente da aplicação Django para gerir o tráfego que vem da internet (porta 80).

**Configurações Críticas:**
- **Static & Media**: Define aliases para as pastas `/static/` e `/media/`. Isso remove a carga do servidor Django, permitindo que o Nginx sirva arquivos diretamente do disco com cabeçalhos de cache otimizados.
- **Suporte a WebSockets**: Configura os headers `Upgrade` e `Connection` necessários para que as conexões do **Django Channels** (Chat e Notificações RT) não caiam e sejam encaminhadas corretamente.
- **Segurança de Cabeçalhos**: Repassa o IP real do cliente (`X-Real-IP`) e o protocolo (`X-Forwarded-Proto`) para que o Django saiba se a requisição é segura e de onde ela vem originalmente.
- **Timeout e Performance**: Define limites de tamanho de upload (`client_max_body_size 20M`) e timeouts de leitura para evitar bloqueios no servidor.

---

## 🚀 Fluxo de Inicialização (Docker Compose)

Quando corres o comando `docker compose up`, o fluxo é o seguinte:

1. O Docker inicia os containers de **PostgreSQL** e **Redis**.
2. O container **Web** (Django) inicia e roda o `entrypoint.sh`.
3. O `entrypoint.sh` trava a inicialização até que o DB e Redis respondam "OK".
4. O `entrypoint.sh` roda as migrações e prepara os estáticos.
5. O container **Nginx** sobe e começa a escutar na porta 80, pronto para enviar pedidos para o container **Web**.

---

> [!TIP]
> Podes consultar as variáveis de ambiente necessárias para que estes scripts funcionem corretamente no arquivo `.env.example` na raiz do projeto.
