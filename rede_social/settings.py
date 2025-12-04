import os
from pathlib import Path
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# SECRET KEY
# -------------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key")

# -------------------------------
# DEBUG
# -------------------------------
DEBUG = config("DEBUG", default=True, cast=bool)

# -------------------------------
# ALLOWED_HOSTS
# -------------------------------
from decouple import config

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",")]
)

print("ALLOWED_HOSTS =", ALLOWED_HOSTS)

# -------------------------------
# INSTALLED APPS
# -------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Seus apps
    "core",
    "usuarios",
    "mensagens",
    # "django_celery_beat",  # se for usar Celery
]

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise para static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # middleware customizado do core
    "core.middleware.HandleGenericExceptionMiddleware",
]

# -------------------------------
# URLS E TEMPLATES
# -------------------------------
ROOT_URLCONF = "rede_social.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Context processor das conversas
                "mensagens.context_processors.conversas_recebidas",
            ],
        },
    },
]

WSGI_APPLICATION = "rede_social.wsgi.application"
ASGI_APPLICATION = "rede_social.asgi.application"  # para channels

# -------------------------------
# DATABASES
# -------------------------------
DATABASES = {
    "default": dj_database_url.parse(
        config(
            "DATABASE_URL",
            default=f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"
        ),
        conn_max_age=600
    )
}

# -------------------------------
# REDIS / CHANNELS
# -------------------------------
REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# -------------------------------
# CELERY (opcional)
# -------------------------------
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_TIMEZONE = "America/Sao_Paulo"

# -------------------------------
# PASSWORD VALIDATION
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------------
# INTERNACIONALIZAÇÃO
# -------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIC FILES
# -------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Diretórios adicionais para static durante desenvolvimento
STATICFILES_DIRS = [BASE_DIR / "static"]

# -------------------------------
# MEDIA FILES
# -------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------
# LOGIN / LOGOUT
# -------------------------------
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

# -------------------------------
# MESSAGES
# -------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# -------------------------------
# E-MAIL
# -------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# -------------------------------
# WHATSAPP
# -------------------------------
WHATSAPP_TOKEN = config("WHATSAPP_TOKEN", default="")
WHATSAPP_PHONE_NUMBER_ID = config("WHATSAPP_PHONE_NUMBER_ID", default="")
WHATSAPP_BUSINESS_ACCOUNT_ID = config("WHATSAPP_BUSINESS_ACCOUNT_ID", default="")

# -------------------------------
# DEFAULT AUTO FIELD
# -------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
