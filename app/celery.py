import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('kwanzaconnect')

# Lê as configurações Celery com prefixo CELERY_ do settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente tasks em todos os apps instalados
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
