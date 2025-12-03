from .models import Mensagem
from django.db.models import Count, Q, Max
from django.contrib.auth.models import User
from usuarios.models import Perfil

def conversas_recebidas(request):
    if not request.user.is_authenticated:
        return {}

    mensagens_agrupadas = (
        Mensagem.objects.filter(Q(destinatario=request.user) | Q(remetente=request.user))
        .exclude(remetente=request.user, destinatario=request.user)
        .values("remetente__id", "remetente__username", "destinatario__id", "destinatario__username")
        .annotate(
            total=Count("id"),
            nao_lidas=Count("id", filter=Q(lida=False, destinatario=request.user)),
            ultima_data=Max("data_envio")
        )
        .order_by("-ultima_data")
    )

    conversas = {}
    total_nao_lidas = 0  # ← CONTAR TODAS
    for m in mensagens_agrupadas:
        if m["nao_lidas"] == 0:
            continue  # pula conversas lidas

        # id e username do outro usuário na conversa
        outro_id = m["remetente__id"] if m["remetente__id"] != request.user.id else m["destinatario__id"]
        outro_username = m["remetente__username"] if m["remetente__id"] != request.user.id else m["destinatario__username"]

        # Pega o perfil do outro usuário para acessar a foto
        try:
            perfil = User.objects.get(id=outro_id).perfil
            foto_url = perfil.foto_perfil.url if perfil.foto_perfil else None
        except (User.DoesNotExist, Perfil.DoesNotExist):
            foto_url = None

        if outro_id not in conversas or m["ultima_data"] > conversas[outro_id]["ultima_data"]:
            conversas[outro_id] = {
                "outro_id": outro_id,
                "outro_username": outro_username,
                "total": m["total"],
                "nao_lidas": m["nao_lidas"],
                "ultima_data": m["ultima_data"],
                "foto_perfil_url": foto_url or "https://via.placeholder.com/60",  # fallback
            }
        total_nao_lidas += m["nao_lidas"]  # ← SOMA

    return {
        "conversas_dropdown": list(conversas.values()),  # nome que você usou no template
        "total_nao_lidas": total_nao_lidas  # ← RETORNE
    }
