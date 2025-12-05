"""
WSGI config for rede_social project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rede_social.settings')

application = get_wsgi_application()

# --------------------------------------------
# AUTO CREATE SUPERUSER (SAFE FOR RENDER)
# --------------------------------------------
import threading

def create_superuser():
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError, ProgrammingError

    try:
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL")

        if (
            os.getenv("AUTO_CREATE_SUPERUSER") == "true"
            and username and password
        ):
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print(">>> Superusuário criado automaticamente.")
            else:
                print(">>> Superusuário já existe.")
    except (OperationalError, ProgrammingError):
        print(">>> Banco ainda não está pronto para criar superusuário.")

# executa em thread para não travar o boot do Gunicorn
threading.Thread(target=create_superuser).start()

