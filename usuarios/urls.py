from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios import views
from . import views 

urlpatterns = [
    # Perfil e edição de perfil do usuário
    
    path('', views.editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views.perfil, name='perfil'),
    path('perfil/<str:username>/editar/', views.editar_perfil, name='editar_perfil'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),

    # Seguir usuário
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),
    
    # Busca
    path('buscar/', views.buscar_usuarios, name='buscar_usuarios'),

    # Autenticação (login, logout, registro, redefinição de senha)
    path('register/', views.register_view, name='register'),
    path("confirmar-email/<uidb64>/<token>/", views.confirmar_email_view, name="confirmar_email"),
    path("dados-pessoais/", views.dados_pessoais_view, name="dados_pessoais"),
    
    path('pagamento/', views.editar_dados_pagamento, name='editar_dados_pagamento'),
    # Login e Logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Redefinição de senha
    path('redefinir-senha/', views.solicitar_redefinicao_senha, name='solicitar_redefinicao_senha'),
    path('redefinir-senha/<uidb64>/<token>/', views.redefinir_senha, name='redefinir_senha'),
]
