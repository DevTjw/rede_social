# usuarios/views_admin.py

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q, Count
from django.db.models.functions import TruncDate

# ==========================================================
#  Verificação de permissão admin
# ==========================================================
only_admin = user_passes_test(lambda u: u.is_superuser or u.is_staff)


# ==========================================================
#  VIEW: Gerenciar usuários inativos (Bootstrap)
# ==========================================================
@only_admin
def admin_ativacao_usuarios_view(request):

    # ==========================================
    # TRATAR POST (ativar / inativar / reenviar e-mail)
    # ==========================================
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        acao = request.POST.get("acao")

        user = User.objects.filter(id=user_id).first()
        if not user:
            messages.error(request, "Usuário não encontrado.")
            return redirect("painel_admin:admin_ativacao_usuarios")

        # --- AÇÃO: ATIVAR ---
        if acao == "ativar":
            user.is_active = True
            user.save()
            messages.success(request, f"Usuário '{user.username}' foi ativado!")
            return redirect("painel_admin:admin_ativacao_usuarios")

        # --- AÇÃO: INATIVAR ---
        elif acao == "inativar":
            user.is_active = False
            user.save()
            messages.success(request, f"Usuário '{user.username}' foi inativado!")
            return redirect("painel_admin:admin_ativacao_usuarios")

        # --- AÇÃO: REENVIAR EMAIL ---
        elif acao == "reenviar_email":
            if user.is_active:
                messages.warning(request, "Usuário ativo não precisa confirmar e-mail.")
                return redirect("painel_admin:admin_ativacao_usuarios")

            reenviar_email_confirmacao(request, user)
            messages.success(request, f"E-mail reenviado para {user.email}")
            return redirect("painel_admin:admin_ativacao_usuarios")

    # ==========================================
    # GET → Filtros
    # ==========================================

    status = request.GET.get("status", "todos")
    q = request.GET.get("q", "")
    data = request.GET.get("data", "")

    users = User.objects.all()

    # Filtro por status
    if status == "ativo":
        users = users.filter(is_active=True)
    elif status == "inativo":
        users = users.filter(is_active=False)

    # Busca por nome/email
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))

    # Filtro por data
    if data:
        users = users.filter(date_joined__date=data)

    users = users.order_by("-date_joined")

    return render(request, "administrativo/admin/ativacao_usuarios.html", {
        "users": users,
        "status": status,
        "filtro_q": q,
        "filtro_data": data,
    })


# ==========================================================
#  Função de REENVIO de email de confirmação
# ==========================================================
def reenviar_email_confirmacao(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    confirm_url = request.build_absolute_uri(
        reverse("confirmar_email", kwargs={"uidb64": uid, "token": token})
    )

    html_message = render_to_string(
        "emails/confirmar_email.html",
        {
            "username": user.username,
            "confirm_url": confirm_url,
            "SITE_NAME": settings.SITE_NAME,
        }
    )
    plain_message = strip_tags(html_message)

    send_mail(
        "Confirme seu e-mail (enviado pelo administrador)",
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


# ==========================================================
#  DASHBOARD ADMIN
# ==========================================================
@only_admin
def admin_dashboard_view(request):

    # Estatísticas por dia
    stats = (
        User.objects.annotate(data=TruncDate("date_joined"))
        .values("data")
        .annotate(total=Count("id"))
        .order_by("data")
    )

    labels = [str(item["data"]) for item in stats]
    values = [item["total"] for item in stats]

    total_ativos = User.objects.filter(is_active=True).count()
    total_inativos = User.objects.filter(is_active=False).count()

    return render(request, "administrativo/admin/dashboard.html", {
        "labels": labels,
        "values": values,
        "ativos": total_ativos,
        "inativos": total_inativos,
    })
