from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import PostForm 
from .models import Post, Comentario
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from usuarios.utils import get_perfil_data
from mensagens.utils import get_conversas
from mensagens.models import Mensagem
from django.core.files import File
from django.conf import settings
import os
from .utils import gerar_imagem_post
from django.urls import reverse
from django.contrib import messages

# ========== PÁGINA INICIAL ==========
def index(request):
    return render(request, 'index.html')

@login_required
def painel(request):
    user = request.user

    # Dados de perfil e conversas
    perfil = get_perfil_data(user)
    conversas = get_conversas(user)

    # Feed
    usuarios_seguidos = User.objects.filter(perfil__seguidores=user)
    posts = Post.objects.filter(
        Q(autor=user) | Q(autor__in=usuarios_seguidos)
    ).annotate(
        num_curtidas=Count('curtidas'),
        num_comentarios=Count('comentarios')
    ).order_by('-data_criacao')[:10]

    # Comentários recentes
    comentarios_recentes = Comentario.objects.filter(
        autor=user
    ).select_related('post').order_by('-data_criacao')[:10]

    # Mensagens recentes
    mensagens_recentes = Mensagem.objects.filter(
        Q(remetente=user) | Q(destinatario=user)
    ).select_related('remetente', 'destinatario').order_by('-data_envio')[:20]

    # Top posts
    top_posts = Post.objects.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas')[:10]

    # Sugestões de usuários
    sugestoes = User.objects.exclude(id=user.id).exclude(id__in=usuarios_seguidos).annotate(
        num_seguidores=Count('perfil__seguidores')
    )

    # Estatísticas rápidas
    estatisticas = {
        'total_posts': Post.objects.filter(autor=user).count(),
        'total_comentarios': Comentario.objects.filter(autor=user).count(),
        'total_curtidas_recebidas': Post.objects.filter(autor=user).annotate(
            num_curtidas=Count('curtidas')
        ).aggregate(total=Sum('num_curtidas'))['total'] or 0,
        'total_mensagens_enviadas': Mensagem.objects.filter(remetente=user).count(),
        'total_mensagens_recebidas': Mensagem.objects.filter(destinatario=user).count(),
    }

    context = {
        'perfil': perfil,
        'conversas': conversas,
        'posts': posts,
        'comentarios_recentes': comentarios_recentes,
        'mensagens_recentes': mensagens_recentes,
        'top_posts': top_posts,
        'sugestoes': sugestoes,
        'estatisticas': estatisticas
    }

    return render(request, 'core/dashboard.html', context)

# ========== PÁGINAS DE ERRO ==========

def erro_404(request, exception):
    return render(request, 'erro.html', {
        'titulo': 'Página não encontrada (404)',
        'mensagem': 'A página que você está procurando não existe.'
    }, status=404)

def erro_500(request):
    return render(request, 'erro.html', {
        'titulo': 'Erro interno do servidor (500)',
        'mensagem': 'Ocorreu um erro inesperado. Tente novamente mais tarde.'
    }, status=500)

def erro_403(request, exception):
    return render(request, 'erro.html', {
        'titulo': 'Acesso negado (403)',
        'mensagem': 'Você não tem permissão para acessar esta página.'
    }, status=403)

def erro_400(request, exception):
    return render(request, 'erro.html', {
        'titulo': 'Requisição inválida (400)',
        'mensagem': 'A requisição não pôde ser entendida pelo servidor.'
    }, status=400)

# ========== FEED E POSTS ==========

def home(request):
    """
    Página inicial pública (visitantes) ou privada (usuários logados).
    Exibe posts do usuário e de quem ele segue.
    """
    context = {}

    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
        except:
            from usuarios.models import Perfil
            perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

        usuarios_seguidos = User.objects.filter(perfil__seguidores=request.user)

        posts = Post.objects.filter(
            Q(autor=request.user) | Q(autor__in=usuarios_seguidos)
        ).order_by('-data_criacao')

        form = PostForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            return redirect('home')

        sugestoes = User.objects.exclude(
            id=request.user.id
        ).exclude(
            id__in=usuarios_seguidos
        )

        context.update({
            'posts': posts,
            'form': form,
            'sugestoes': sugestoes
        })

    return render(request, 'core/home.html', context)

@login_required
def feed(request):
    """
    Feed principal — mostra posts do usuário e de quem ele segue.
    """
    try:
        perfil = request.user.perfil
    except:
        from usuarios.models import Perfil
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    usuarios_seguidos = User.objects.filter(perfil__seguidores=request.user)
    posts = Post.objects.filter(
        Q(autor=request.user) | Q(autor__in=usuarios_seguidos)
    ).order_by('-data_criacao')

    sugestoes = User.objects.exclude(id=request.user.id).exclude(id__in=usuarios_seguidos)

    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.autor = request.user
        post.save()
        return redirect('core:feed')

    return render(request, 'core/feed.html', {
        'posts': posts,
        'form': form,
        'sugestoes': sugestoes
    })

@login_required
def deletar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, autor=request.user)
    post.delete()
    return redirect('core:feed')

@login_required
def curtir_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.curtidas.filter(id=request.user.id).exists():
        post.curtidas.remove(request.user)
        action = 'unlike'
    else:
        post.curtidas.add(request.user)
        action = 'like'

    return JsonResponse({
        'success': True,
        'action': action,
        'like_count': post.curtidas.count()
    })


# ========== PREPARAR IMAGEM DE COMPARTILHAMENTO ==========
@login_required
def preparar_compartilhamento(request, post_id):
    '''
    Docstring para preparar_compartilhamento
    :param request: 
    :param post_id: Descrição
    :return: JsonResponse com sucesso e URL do post
    '''
    post = get_object_or_404(Post, id=post_id)

    if not post.imagem_share:
        caminho_relativo = gerar_imagem_post(post)
        caminho_absoluto = os.path.join(settings.MEDIA_ROOT, caminho_relativo)

        with open(caminho_absoluto, "rb") as f:
            post.imagem_share.save(
                os.path.basename(caminho_absoluto),
                File(f),
                save=True
            )

    return JsonResponse({
        "success": True,
        "url": request.build_absolute_uri(
            reverse("core:post_detail", args=[post.id])
        )
    })

# ========== COMPARTILHAR POST ==========
@login_required
def compartilhar_post(request, id):
    '''
    Docstring para compartilhar_post
    
    :param request: Descrição
    :param id: Descrição
    '''
    post = get_object_or_404(Post, id=id, autor=request.user)

    if not post.imagem_share:
        caminho_relativo = gerar_imagem_post(post)
        caminho_absoluto = os.path.join(settings.MEDIA_ROOT, caminho_relativo)

        with open(caminho_absoluto, "rb") as f:
            post.imagem_share.save(
                os.path.basename(caminho_absoluto),
                File(f),
                save=True
            )

    return redirect("post_detail", id=post.id)

# =========== Post publica ================
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'core/post_detail.html', {'post': post})

# ========== COMPARTILHAR POST VIA NOTIFICAÇÃO interna ==========
def garantir_imagem_share(post):
    """
    Garante que o post tenha imagem para compartilhamento.
    Prioridade:
    1️⃣ Imagem original do post
    2️⃣ Imagem gerada automaticamente
    """

    # 🔹 Se o post JÁ TEM imagem, usa ela direto
    if post.imagem:
        return post.imagem.url

    # 🔹 Caso contrário, gera imagem de compartilhamento
    if not post.imagem_share:
        from core.utils import gerar_imagem_post
        import os
        from django.conf import settings
        from django.core.files import File

        caminho_relativo = gerar_imagem_post(post)
        caminho_absoluto = os.path.join(settings.MEDIA_ROOT, caminho_relativo)

        with open(caminho_absoluto, "rb") as f:
            post.imagem_share.save(
                os.path.basename(caminho_absoluto),
                File(f),
                save=True
            )

    return post.imagem_share.url

@login_required
def notificar_post(request, post_id, username):
    from django.urls import reverse
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    from core.models import Post
    from mensagens.models import Mensagem
    from django.contrib.auth.models import User

    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    post = get_object_or_404(Post, id=post_id)
    destinatario = get_object_or_404(User, username=username)
    remetente = request.user

    if destinatario == remetente:
        return JsonResponse({'error': 'Você não pode enviar mensagem para si mesmo.'}, status=400)

    # 🔹 Garante imagem de compartilhamento
    imagem_url = garantir_imagem_share(post)

    # 🔹 URL absoluta para o post
    post_url = request.build_absolute_uri(
        reverse("core:post_detail", args=[post.id])
    )

    # 🔹 Conteúdo da mensagem com preview HTML
    conteudo_html = f"""
<div class="post-box">
    <h4>📢 {remetente.username} compartilhou um post com você</h4>
    <img src="{imagem_url}" style="width:100%;max-width:480px;border-radius:12px;margin-bottom:10px;">
    <p>📝 {getattr(post, 'titulo', 'Post compartilhado')}</p>
    <a href="{post_url}" class="btn btn-primary" target="_blank">🔗 Ver post</a>
</div>
"""

    # 🔹 Cria a mensagem interna
    Mensagem.objects.create(
        remetente=remetente,
        destinatario=destinatario,
        conteudo=conteudo_html
    )

    return JsonResponse({'success': True})
 

# ========== COMENTÁRIOS ==========
@login_required
def adicionar_comentario(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto = data.get('texto', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Dados JSON inválidos'})

        if texto:
            comentario = Comentario.objects.create(
                post=post,
                autor=request.user,
                texto=texto
            )

            # Se quiser retornar a foto do perfil (opcional)
            foto_url = request.user.perfil.foto_perfil.url if hasattr(request.user, 'perfil') and request.user.perfil.foto_perfil else ''

            return JsonResponse({
                'success': True,
                'autor': comentario.autor.username,
                'texto': comentario.texto,
                'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'foto_perfil': foto_url
            })

    return JsonResponse({'success': False, 'error': 'Método inválido'})

@login_required
@require_POST
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.autor != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permissão negada.'}, status=403)

    novo_texto = request.POST.get('texto', '').strip()
    if not novo_texto:
        return JsonResponse({'success': False, 'error': 'Texto não pode ser vazio.'}, status=400)

    comentario.texto = novo_texto
    comentario.save()

    return JsonResponse({
        'success': True,
        'texto': comentario.texto,
        'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M')
    })

@login_required
@require_POST
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.autor == request.user or request.user.is_staff:
        comentario.delete()
        return JsonResponse({'success': True})  # <-- CORRIGIDO
    else:
        return JsonResponse({
            'success': False,
            'error': 'Você não tem permissão para excluir este comentário.'
        }, status=403)

# ========== SUGESTÕES DE USUÁRIOS ==========
@login_required
def feed_sugestoes(request):
    try:
        perfil_usuario = request.user.perfil
    except:
        return render(request, 'erro.html', {
            'message': 'Seu perfil ainda não foi criado. Por favor, contate o administrador.'
        })

    todos_usuarios = User.objects.exclude(id=request.user.id)
    sugestoes = []

    for u in todos_usuarios:
        try:
            u.ja_segue = u.perfil.seguidores.filter(id=request.user.id).exists()
        except:
            u.ja_segue = False
        sugestoes.append(u)

    return render(request, 'core/feed_sugestoes.html', {'sugestoes': sugestoes})
