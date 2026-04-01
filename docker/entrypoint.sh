#!/bin/bash
set -e

echo "Aguardando PostgreSQL em $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "PostgreSQL disponível."

echo "Aguardando Redis..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "Redis disponível."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

# Criar superuser automaticamente se não existir
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
        full_name='Admin'
    )
    print('Superuser criado.')
else:
    print('Superuser já existe.')
"

exec "$@"