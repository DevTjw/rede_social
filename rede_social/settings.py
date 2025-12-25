"""
Django settings for rede_social project.
"""

from pathlib import Path
import os
from decouple import config
# import dj_database_url
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================================
# 🔐 SEGURANÇA
# =====================================================================

# Nunca deixe a SECRET_KEY exposta no código!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key")

# DEBUG
# -------------------------------
DEBUG = config("DEBUG", default=True, cast=bool)

# ALLOWED_HOSTS seguro e funcional
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]



# =====================================================================
# 📦 APPS INSTALADOS
# =====================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'core',
    'usuarios',
    'mensagens',
    'channels',
    # Celery (descomente se usar)
    'django_celery_beat',
]

# =====================================================================
# 🧱 MIDDLEWARE
# =====================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware customizado
    'core.middleware.HandleGenericExceptionMiddleware',
]

# =====================================================================
# 🔗 URL / WSGI / ASGI
# =====================================================================

ROOT_URLCONF = 'rede_social.urls'
WSGI_APPLICATION = 'rede_social.wsgi.application'
ASGI_APPLICATION = 'rede_social.asgi.application'

# =====================================================================
# 🖥️ TEMPLATES
# =====================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'mensagens.context_processors.conversas_recebidas',
                'usuarios.context_processors.site_info',
            ],
        },
    },
]

# =====================================================================
# 🗄️ DATABASE (dev e produção automáticos)
# =====================================================================

USE_SQLITE = os.getenv("USE_SQLITE", "True") == "True"

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': os.getenv("DB_HOST", "localhost"),
            'PORT': os.getenv("DB_PORT", "5432"),
        }
    }


# =====================================================================
# 📧 EMAIL SMTP
# =====================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# =====================================================================
# 🟢 REDIS
# =====================================================================

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, int(REDIS_PORT))],
        },
    },
}

# =====================================================================
# 🚀 CELERY
# =====================================================================

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_TIMEZONE = 'America/Sao_Paulo'

SITE_NAME = os.getenv("SITE_NAME", "LABYSIM")
SITE_URL = os.getenv("SITE_URL", "https://labysim.onrender.com")
SITE_SLOGAN = os.getenv(
    "SITE_SLOGAN",
    "A rede social da Web Pública Gratuita mantida por donativos"
)



# =====================================================================
# 🌍 INTERNACIONALIZAÇÃO
# =====================================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# =====================================================================
# 🎨 ARQUIVOS ESTÁTICOS
# =====================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =====================================================================
# 📁 ARQUIVOS DE MÍDIA (uploads)
# =====================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# =====================================================================
# 🔐 AUTENTICAÇÃO
# =====================================================================

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home'

# =====================================================================
# 🔔 MENSAGENS (Bootstrap)
# =====================================================================

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

SECURE_CROSS_ORIGIN_OPENER_POLICY = None



# ===============================
# 📟 Configurações de Log
# ===============================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "ERROR",
        },
    },
}
# ===============================
# FIM DO ARQUIVO settings.py
# ===============================