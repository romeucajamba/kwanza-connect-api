#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "PostgreSQL disponível."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"