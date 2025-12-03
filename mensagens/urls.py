from django.urls import path
from mensagens import views

app_name = 'mensagens'
urlpatterns = [
       
   # Caixa de entrada (lista de conversas)
    path('', views.caixa_entrada, name='caixa_entrada'),

    # Lista todos os usuários disponíveis para conversar
    path('usuarios/', views.lista_usuarios, name='listar_usuarios'),

    # Exibe a lista de usuários
    path('chat/', views.lista_usuarios, name='lista_usuarios'),
    # Inicia um chat com outro usuário
    path('chat/<str:destinatario_username>/', views.chat_view, name='chat'),
    # Nome diferente para a caixa de chat, se realmente necessário
    path('chat_box/<str:chat_box_name>/', views.chat_view, name='chat_box'),

    # Conversa antiga ou privada (se for necessário manter)
    path('conversa/<str:username>/', views.conversa, name='conversa'),

    # Enviar mensagem para um usuário específico
    path('enviar/<str:username>/', views.enviar_mensagem, name='enviar_mensagem'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
   path('buscar_seguidores/', views.buscar_seguidores, name='buscar_seguidores'), 

    # Rota para envio de mensagem sem destinatário pré-definido (ex: formulário geral)
    path('enviar/', views.enviar_mensagem, name='enviar_mensagem_geral'),

    
    path('mensagens/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('mensagens/enviar/<str:username>/', views.enviar_mensagem, name='enviar_mensagem_com_usuario'),

    #  Rota de edição
    path('mensagem/<int:pk>/editar/', views.editar_mensagem, name='editar_mensagem'),
   
    # Chat flutuante
    path('buscar_usuarios_gen/', views.buscar_usuarios_gen, name='buscar_usuarios_gen'),
    path('conversa/<str:username>/atualizar/', views.conversa_atualizar, name='conversa_atualizar'),
    path('conversa/<str:username>/enviar/', views.conversa_enviar, name='conversa_enviar'),
    path('mensagem/<int:id>/editar/', views.mensagem_editar, name='mensagem_editar'),

    # Lista lateral de seguidores
    path('atualizar_seguidores/', views.atualizar_seguidores, name='atualizar_seguidores'),
    ]

 
