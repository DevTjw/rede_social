from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Perfil, DadosPessoais
from .forms import RegistroForm, PerfilForm, UserForm, DadosPessoaisForm
from django.db import IntegrityError
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import authenticate, login
from .forms import DadosPagamentoForm
from .models import DadosPagamento
from .models import Perfil
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

#  View de login
def login_view(request):
    
    # ⛔ Se já estiver logado, redireciona para "/"
    if request.user.is_authenticated:
        messages.info(request, "Você já está logado.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if remember_me:
                request.session.set_expiry(60 * 60 * 24)  # 24 horas
            else:
                request.session.set_expiry(0)  # expira ao fechar o navegador

            return redirect('home')

        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'registrationn/login.html')

#  Logout 
def logout_view(request):
    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "Você saiu da sua conta com sucesso.")
        return redirect("login")
    # Redirecionar caso acesse via GET
    return redirect("home")

#  View de registro
def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Você já está logado.")
        return redirect("home")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                # 🔹 Cria usuário inativo
                user = form.save(commit=False)
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.is_active = False
                user.save()

                # 🔹 Cria perfil vinculado
                Perfil.objects.get_or_create(usuario=user)

                # 🔹 Gera token e UID
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                current_site = get_current_site(request)
                confirm_url = request.build_absolute_uri(
                    reverse("confirmar_email", kwargs={"uidb64": uid, "token": token})
                )

                # 🔹 Renderiza HTML futurista
                html_message = render_to_string(
                    "emails/confirmar_email.html",
                    {
                        "username": user.username,
                        "confirm_url": confirm_url,
                        "SITE_NAME": current_site.name,
                    }
                )
                plain_message = strip_tags(html_message)

                # 🔹 Envia email
                try:
                    send_mail(
                        subject="Confirme seu email para ativar sua conta",
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except BadHeaderError:
                    messages.error(request, "Erro no envio do e-mail: cabeçalho inválido.")
                    user.delete()  # Remove usuário incompleto
                    return redirect("register")
                except Exception as e:
                    messages.error(request, f"Erro ao enviar e-mail: {e}")
                    user.delete()  # Remove usuário incompleto
                    return redirect("register")

                messages.info(
                    request,
                    f"Enviamos um e-mail para {user.email}. Clique no link para ativar sua conta."
                )
                return redirect("login")

            except IntegrityError:
                messages.error(request, "Este nome de usuário ou e-mail já está em uso.")
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao criar a conta: {e}")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = RegistroForm()

    return render(request, "registration/register.html", {"form": form})

# confirmar email
def confirmar_email_view(request, uidb64, token):
    try:
        # Decodifica o ID do usuário
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Ativa a conta
        user.is_active = True
        user.save()
        messages.success(request, "Email confirmado! Agora você pode fazer login.")
        return redirect("login")
    else:
        messages.error(request, "Link inválido ou expirado.")
        return redirect("register")

#  Solicitar redefinição de senha
def solicitar_redefinicao_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = User.objects.get(email=email)
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            link = request.build_absolute_uri(f'/usuarios/redefinir-senha/{uid}/{token}/')

            # 🔹 Cria o conteúdo HTML e texto puro
            contexto = {
                'nome': usuario.first_name or usuario.username,
                'link': link,
            }

            html_message = render_to_string('emails/redefinir_senha.html', contexto)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f'Redefinição de Senha - {settings.SITE_NAME}',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, 'Um link de redefinição foi enviado para seu e-mail.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'Nenhuma conta com este e-mail foi encontrada.')

    return render(request, 'registration/solicitar_redefinicao_senha.html')

#  Redefinir senha
def redefinir_senha(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            senha1 = request.POST.get('senha1')
            senha2 = request.POST.get('senha2')
            if senha1 == senha2:
                usuario.set_password(senha1)
                usuario.save()
                messages.success(request, 'Senha redefinida com sucesso. Faça login.')
                return redirect('login')
            else:
                messages.error(request, 'As senhas não coincidem.')

        return render(request, 'registration/redefinir_senha.html', {'valido': True})
    else:
        return render(request, 'registration/redefinir_senha.html', {'valido': False})
    
# Dados pessoais
@login_required
def dados_pessoais_view(request):
    try:
        dados = request.user.dados_pessoais
    except DadosPessoais.DoesNotExist:
        dados = None

    if request.method == "POST":
        form = DadosPessoaisForm(request.POST, instance=dados, usuario=request.user)
        if form.is_valid():
            dados_pessoais = form.save(commit=False)
            dados_pessoais.usuario = request.user
            dados_pessoais.save()
            messages.success(request, "Seus dados pessoais foram salvos com sucesso!")
            return redirect('perfil', username=request.user.username)
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = DadosPessoaisForm(instance=dados, usuario=request.user)  # ← passou o usuario aqui

    return render(request, "usuarios/dados_pessoais.html", {"form": form})

@login_required
def editar_dados_pagamento(request):
    try:
        dados_pagamento = request.user.dados_pagamento
    except DadosPagamento.DoesNotExist:
        dados_pagamento = DadosPagamento(usuario=request.user)

    if request.method == 'POST':
        form = DadosPagamentoForm(request.POST, instance=dados_pagamento)
        if form.is_valid():
            form.save()
            return redirect('perfil', username=request.user.username)  # redirecione para a página do perfil
    else:
        form = DadosPagamentoForm(instance=dados_pagamento)

    return render(request, 'usuarios/pagamento.html', {'form': form})

#  Perfil do usuário
@login_required
def perfil(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil, _ = Perfil.objects.get_or_create(usuario=usuario)

    posts = usuario.post_set.all().order_by('-data_criacao')
    seguidores_count = perfil.seguidores.count()
    seguindo_count = User.objects.filter(perfil__seguidores=usuario).count()

    segue = perfil.seguidores.filter(id=request.user.id).exists()

    return render(request, 'core/perfil.html', {
        'usuario_perfil': usuario,
        'posts': posts,
        'seguidores_count': seguidores_count,
        'seguindo_count': seguindo_count,
        'segue': segue
    })

#  Edição de perfil
@login_required
def editar_perfil(request):
    perfil_instance, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil_instance)

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('perfil', username=request.user.username)
        else:
            messages.error(request, "Verifique os campos e tente novamente.")
    else:
        user_form = UserForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil_instance)

    return render(request, 'core/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form
    })

#  Buscar usuários
@login_required
def buscar_usuarios(request):
    query = request.GET.get('q', '')
    if query:
        usuarios = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    else:
        usuarios = User.objects.none()

    return render(request, 'core/buscar_usuarios.html', {
        'usuarios': usuarios,
        'query': query
    })

#  Seguir / deixar de seguir
@login_required
def seguir_usuario(request, username):
    if request.method != "POST":
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    usuario = get_object_or_404(User, username=username)

    if request.user == usuario:
        return JsonResponse({'error': 'Você não pode seguir a si mesmo'}, status=400)

    perfil = usuario.perfil
    if perfil.seguidores.filter(id=request.user.id).exists():
        perfil.seguidores.remove(request.user)
        seguindo = False
    else:
        perfil.seguidores.add(request.user)
        seguindo = True

    return JsonResponse({
        'seguindo': seguindo,
        'seguidores_count': perfil.seguidores.count()
    })
