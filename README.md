# Subir todos os containers
docker compose up --build

# Criar superuser dentro do container
docker compose exec web python manage.py createsuperuser

# Ver logs
docker compose logs -f web

# Rodar migrações manualmente
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Aceder ao shell Django
docker compose exec web python manage.py shell

# Parar tudo
docker compose down