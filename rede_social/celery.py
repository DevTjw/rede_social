import os
from celery import Celery

# Define o settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rede_social.settings')

app = Celery('rede_social')

# Configurações do Django (prefixo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks.py em apps do Django
app.autodiscover_tasks()

# Configuração do broker e backend Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

app.conf.broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
app.conf.result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

# Outras boas práticas
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'UTC'
app.conf.enable_utc = True
