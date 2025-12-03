from django.urls import path
from core import views
from core.views import deletar_post

app_name = "core" 

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
     # path('painel/', views.painel_geral, name="painel_geral"),
    path('painel/', views.painel, name="painel"),

    # Feed principal
    path('feed/', views.feed, name='feed'),
    path('feed_sugestoes/', views.feed_sugestoes, name='feed_sugestoes'),

    # Postagens
    path('post/<int:post_id>/deletar/', deletar_post, name='deletar_post'),
    path('post/<int:post_id>/curtir/', views.curtir_post, name='curtir_post'),
    path('post/<int:post_id>/comentar/', views.adicionar_comentario, name='adicionar_comentario'),

    # Comentários
    path('comentario/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentario/<int:comentario_id>/excluir/', views.excluir_comentario, name='excluir_comentario'),
    path('core/comentario/<int:comentario_id>/excluir/', views.excluir_comentario, name='excluir_comentario'),

    # Teste de erro
    path('erro-test/', lambda request: views.generic_error_view(request, "Erro de teste!")),
]
