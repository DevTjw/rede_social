"""
WSGI config for rede_social project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import threading
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rede_social.settings")

application = get_wsgi_application()

# ==========================================================
# AUTO CREATE SUPERUSER (SAFE FOR PRODUCTION HOSTING)
# ==========================================================

def auto_create_superuser():
    """
    Cria superusuário automaticamente se variáveis de ambiente estiverem definidas.
    Seguro para ambientes como Render, Railway e Gunicorn.
    """
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError, ProgrammingError

    try:
        User = get_user_model()

        flag = os.getenv("AUTO_CREATE_SUPERUSER", "false").lower()
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL")

        # só roda se as variáveis estiverem presentes
        if flag == "true" and username and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email,
                )
                print(">>> [WSGI] Superusuário criado automaticamente.")
            else:
                print(">>> [WSGI] Superusuário já existe, ignorando.")
        else:
            print(">>> [WSGI] AUTO_CREATE_SUPERUSER está desativado.")

    except (OperationalError, ProgrammingError):
        print(">>> [WSGI] Banco não está pronto. Não foi possível criar o superusuário.")

# roda em thread para evitar travar gunicorn
threading.Thread(target=auto_create_superuser, daemon=True).start()
