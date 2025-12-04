"""
Django settings for rede_social project.
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages
from dotenv import load_dotenv
from decouple import config

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# 🔐 SECURITY — SECRET KEY, DEBUG, HOSTS
# ============================================================

SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key")

DEBUG = config("DEBUG", default=False, cast=bool)

# Permite vários hosts separados por vírgula
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=".onrender.com,localhost,127.0.0.1").split(",")

# ============================================================
# 🔌 APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'usuarios',
    'mensagens',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.HandleGenericExceptionMiddleware',
]

ROOT_URLCONF = 'rede_social.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'mensagens.context_processors.conversas_recebidas',
            ],
        },
    },
]

WSGI_APPLICATION = 'rede_social.wsgi.application'
ASGI_APPLICATION = 'rede_social.asgi.application'


# ============================================================
# 📦 DATABASE
# ============================================================

# Se estiver no Render → PostgreSQL automático
if config("RENDER", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }
else:
    # Local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================================
# 📡 REDIS & CHANNELS (opcional)
# ============================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(config("REDIS_HOST", default="localhost"), 6379)],
        },
    },
}

CELERY_BROKER_URL = f"redis://{config('REDIS_HOST', default='localhost')}:6379/0"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL


# ============================================================
# 📩 EMAIL
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default=None)
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=None)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=None)


# ============================================================
# 🌐 SITE URL
# ============================================================

SITE_URL = config("SITE_URL", default="http://localhost:8000")


# ============================================================
# 🔑 WHATSAPP
# ============================================================

WHATSAPP_TOKEN = config('WHATSAPP_TOKEN', default=None)
WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default=None)
WHATSAPP_BUSINESS_ACCOUNT_ID = config('WHATSAPP_BUSINESS_ACCOUNT_ID', default=None)


# ============================================================
# 🔐 PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# 🌍 LANGUAGE & TIMEZONE
# ============================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ============================================================
# 🎨 STATIC FILES
# ============================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ============================================================
# 📁 MEDIA FILES
# ============================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ============================================================
# 🔐 AUTH & LOGIN
# ============================================================

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home'


# ============================================================
# MESSAGES
# ============================================================

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

SECURE_CROSS_ORIGIN_OPENER_POLICY = None
