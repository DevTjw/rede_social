# usuarios/urls_admin.py
from django.urls import path
from .views_admin import admin_ativacao_usuarios_view, admin_dashboard_view, reenviar_email_confirmacao

app_name = "painel_admin"

urlpatterns = [
    path("ativacao-usuarios/", admin_ativacao_usuarios_view, name="admin_ativacao_usuarios"),
    path( "confirmar-email/<uidb64>/<token>/", reenviar_email_confirmacao, name="confirmar_email"),
    path("dashboard/", admin_dashboard_view, name="admin_dashboard"),
]