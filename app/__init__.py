# Garante que o Celery é carregado quando o Django arranca,
# para que os decoradores @shared_task usem esta app.
from .celery import app as celery_app

__all__ = ('celery_app',)
