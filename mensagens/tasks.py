from django.conf import settings
from celery import shared_task

# -------------------------------------------------------------
# Função auxiliar para gerar HTML da foto do profissional
# -------------------------------------------------------------
def gerar_foto_html(profissional):
    if profissional and getattr(profissional, 'foto', None):
        try:
            foto_rel = profissional.foto.url  # /media/profissionais/xxx.jpg
            base_url = settings.SITE_URL.rstrip("/")  # https://seudominio.com
            foto_url = f"{base_url}{foto_rel}"        # URL absoluta

            return f'<img src="{foto_url}" style="width:50px;height:50px;border-radius:50%;margin-right:10px;">'
        except ValueError:
            return ""
    return ""
