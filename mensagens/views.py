from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Max, Case, When, IntegerField
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Mensagem
from .forms import MensagemForm
from usuarios.models import Perfil, Seguimento  
from mensagens.models import Mensagem
from django.views.decorators.http import require_POST

# inicio de webSockert
@login_required
def chat_view(request, destinatario_username):
    """
    Abre a sala de chat entre o usuário logado e o destinatário
    """
    remetente = request.user.username
    destinatario = destinatario_username

    # gerar nome único da sala
    chat_box_name = "_".join(sorted([remetente, destinatario]))

    return render(request, "mensagens/chatbox.html", {
        "chat_box_name": chat_box_name,
        "remetente": remetente,
        "destinatario": destinatario,
    })

@login_required
def lista_usuarios(request):
    """
    Lista todos os usuários (menos o logado) para iniciar uma conversa
    """
    # Anota a quantidade de mensagens não lidas de cada remetente para o usuário logado
    usuarios = User.objects.exclude(id=request.user.id)  # ou .all() se quiser incluir o usuário atual

    usuarios = usuarios.annotate(
        total_nao_lidas=Count(
            'mensagens_recebidas',
            filter=Q(mensagens_recebidas__destinatario=request.user, mensagens_recebidas__lida=False)
        )
    )

    return render(request, 'mensagens/lista_usuarios.html', {'usuarios': usuarios})

#========= CAIXA DE ENTRADA =========
#=========
@login_required
def caixa_entrada(request):
    mensagens_agrupadas = (
        Mensagem.objects.filter(Q(destinatario=request.user) | Q(remetente=request.user))
        .exclude(remetente=request.user, destinatario=request.user)
        .values(
            "remetente__id", "remetente__username",
            "destinatario__id", "destinatario__username"
        )
        .annotate(
            total=Count("id"),
            nao_lidas=Count("id", filter=Q(lida=False, destinatario=request.user)),
            ultima_data=Max("data_envio")
        )
        .order_by("-ultima_data")
    )

    conversas = {}
    for m in mensagens_agrupadas:
        outro_id = m["remetente__id"] if m["remetente__id"] != request.user.id else m["destinatario__id"]
        outro_username = (
            m["remetente__username"]
            if m["remetente__id"] != request.user.id
            else m["destinatario__username"]
        )
        #  Buscar o outro usuário e tentar pegar a foto
        try:
            outro_user = User.objects.get(id=outro_id)
            foto = getattr(outro_user.perfil, 'foto_perfil', None)

            if foto and hasattr(foto, 'url'):
                outro_foto = foto.url
            else:
                outro_foto = None

        except (User.DoesNotExist, AttributeError):
            outro_foto = None

        # Atualizar conversa
        if outro_id not in conversas or m["ultima_data"] > conversas[outro_id]["ultima_data"]:
            conversas[outro_id] = {
                "outro_id": outro_id,
                "outro_username": outro_username,
                "outro_foto": outro_foto,  #  aqui adicionamos a URL da imagem
                "total": m["total"],
                "nao_lidas": m["nao_lidas"],
                "ultima_data": m["ultima_data"],
            }

    return render(request, "mensagens/caixa_entrada.html", {"conversas": conversas.values()})

# Exibir histórico de conversa
@login_required
def conversa(request, username):
    outro_usuario = get_object_or_404(User, username=username)

    mensagens = Mensagem.objects.filter(
        Q(remetente=request.user, destinatario=outro_usuario) |
        Q(remetente=outro_usuario, destinatario=request.user)
    ).order_by('data_envio')

    # Marca mensagens recebidas como lidas
    Mensagem.objects.filter(
        remetente=outro_usuario,
        destinatario=request.user,
        lida=False
    ).update(lida=True)

    # Envio de nova mensagem direto da conversa
    if request.method == 'POST':
        conteudo = request.POST.get('conteudo', '').strip()
        if conteudo:
            if outro_usuario == request.user:
                messages.error(request, "Você não pode enviar mensagens para si mesmo.")
            else:
                Mensagem.objects.create(
                    remetente=request.user,
                    destinatario=outro_usuario,
                    conteudo=conteudo
                )
                messages.success(request, "Mensagem enviada!")
        return redirect('mensagens:conversa', username=outro_usuario.username)

    return render(request, 'mensagens/chat_usuario.html', {
        'mensagens': mensagens,
        'outro_usuario': outro_usuario
    })

# Envio de mensagem direta (com ou sem destinatário)
@login_required
def enviar_mensagem(request):
    perfil_atual = request.user.perfil
    seguidores = perfil_atual.seguidores.all()  # pega todos os seguidores

    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.remetente = request.user

            if msg.destinatario == request.user:
                messages.error(request, "Você não pode enviar mensagens para si mesmo.")
                return redirect('mensagens:enviar_mensagem')

            msg.save()
            messages.success(request, f"Mensagem enviada para {msg.destinatario.username}!")
            return redirect('mensagens:conversa', msg.destinatario.username)
    else:
        form = MensagemForm()

    context = {
        'seguidores': seguidores,
        'form': form,
    }
    return render(request, 'mensagens/enviar_mensagem.html', context)

@login_required
def buscar_usuarios(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)

    usuarios = User.objects.filter(username__icontains=q)[:10]
    data = []
    for u in usuarios:
        perfil = getattr(u, 'perfil', None)
        data.append({
            'username': u.username,
            'nome': u.get_full_name() or u.username,
            'imagem_url': perfil.imagem.url if perfil and perfil.imagem else '/static/images/default-profile.png',
        })
    return JsonResponse(data, safe=False)

@login_required
def buscar_seguidores(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)

    perfil_atual = request.user.perfil
    seguidores_qs = perfil_atual.seguidores.filter(username__icontains=q)[:10]

    data = []
    for u in seguidores_qs:
        perfil = getattr(u, 'perfil', None)
        data.append({
            'username': u.username,
            'nome': u.get_full_name() or u.username,
            'imagem_url': perfil.imagem.url if perfil and perfil.imagem else '/static/images/default-profile.png',
        })
    return JsonResponse(data, safe=False)

# Editar mensagem via AJAX
@login_required
@require_POST
def editar_mensagem(request, pk):
    msg = get_object_or_404(Mensagem, pk=pk, remetente=request.user)  # Só o remetente pode editar
    novo_conteudo = request.POST.get('conteudo', '').strip()

    if not novo_conteudo:
        return JsonResponse({'error': 'Conteúdo não pode ser vazio'}, status=400)

    msg.conteudo = novo_conteudo
    msg.editado = True
    msg.save()

    return JsonResponse({
        'id': msg.id,
        'conteudo': msg.conteudo,
        'editado': msg.editado,
        'data_envio': msg.data_envio.strftime("%d/%m/%Y %H:%M")
    })

# =====================================================
# FUNÇÃO AUXILIAR — CONVERTE USER EM JSON
# =====================================================
# NÃO É VIEWS , NÃO NECESSITA 
def usuario_to_json(u):
    perfil = getattr(u, "perfil", None)
    imagem_url = perfil.foto_perfil.url if perfil and perfil.foto_perfil else "/static/images/default-profile.png"
    return {
        "username": u.username,
        "nome": u.get_full_name() or u.username,
        "imagem_url": imagem_url,
    }

# =====================================================
# BUSCA GENÉRICA DE USUÁRIOS (seguidores / seguindo / todos)
# =====================================================
@login_required
def buscar_usuarios_gen(request):
    tipo = request.GET.get("tipo", "todos")
    q = request.GET.get("q", "").strip()
    limite = int(request.GET.get("limite", 50))
    user = request.user

    if tipo == "seguidores":
        # Quem segue o request.user
        qs = User.objects.filter(perfil__seguidores=user)
    elif tipo == "seguindo":
        # Quem o request.user segue
        try:
            seguindo_ids = user.perfil.seguidores.values_list("id", flat=True)
            qs = User.objects.filter(id__in=seguindo_ids)
        except:
            qs = User.objects.none()
    else:  # todos
        qs = User.objects.exclude(id=user.id)

    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    qs = qs.distinct()[:limite]

    data = [usuario_to_json(u) for u in qs]
    return JsonResponse(data, safe=False)

# =====================================================
# LISTA LATERAL DE SEGUIDORES
# =====================================================
@login_required
def atualizar_seguidores(request):
    # Correto: seguidores = quem segue o usuário
    seguidores = User.objects.filter(seguindo_users__seguindo=request.user)

    data = [usuario_to_json(u) for u in seguidores]
    return JsonResponse({"seguidores": data})

# =====================================================
# CONVERSA — CARREGAR MENSAGENS ajax
# =====================================================
@login_required
def conversa_atualizar(request, username):
    outro = get_object_or_404(User, username=username)
    user = request.user

    msgs = Mensagem.objects.filter(
        Q(remetente=user, destinatario=outro) |
        Q(remetente=outro, destinatario=user)
    ).order_by("data_envio")

    data = [{
        "id": m.id,
        "conteudo": m.conteudo,
        "data_envio": m.data_envio.strftime("%d/%m/%Y %H:%M"),
        "editado": m.editado,
        "proprio": m.remetente == user
    } for m in msgs]

    return JsonResponse({"mensagens": data})

# =====================================================
# ENVIAR MENSAGEM
# =====================================================
@login_required
@require_POST
def conversa_enviar(request, username):
    outro = get_object_or_404(User, username=username)
    texto = request.POST.get("conteudo", "").strip()

    if not texto:
        return JsonResponse({"erro": "Mensagem vazia"}, status=400)

    Mensagem.objects.create(
        remetente=request.user,
        destinatario=outro,
        conteudo=texto
    )

    return JsonResponse({"ok": True})

# =====================================================
# EDITAR MENSAGEM
# =====================================================
@login_required
@require_POST
def mensagem_editar(request, id):
    msg = get_object_or_404(Mensagem, id=id, remetente=request.user)
    novo = request.POST.get("conteudo", "").strip()

    if not novo:
        return JsonResponse({"erro": "Mensagem vazia"}, status=400)

    msg.conteudo = novo
    msg.editado = True
    msg.save()

    return JsonResponse({
        "id": msg.id,
        "conteudo": msg.conteudo,
        "data_envio": msg.data_envio.strftime("%d/%m/%Y %H:%M"),
        "editado": True
    })
