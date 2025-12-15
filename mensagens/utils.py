from django.db.models import Q, Count, Max
from django.contrib.auth.models import User
from .models import Mensagem


def get_conversas(user):
    mensagens_agrupadas = (
        Mensagem.objects.filter(Q(destinatario=user) | Q(remetente=user))
        .exclude(remetente=user, destinatario=user)
        .values("remetente__id", "remetente__username", "destinatario__id", "destinatario__username")
        .annotate(
            total=Count("id"),
            nao_lidas=Count("id", filter=Q(lida=False, destinatario=user)),
            ultima_data=Max("data_envio")
        )
        .order_by("-ultima_data")
    )

    conversas = {}
    for m in mensagens_agrupadas:
        outro_id = m["remetente__id"] if m["remetente__id"] != user.id else m["destinatario__id"]
        outro_username = (
            m["remetente__username"]
            if m["remetente__id"] != user.id
            else m["destinatario__username"]
        )

        try:
            outro_user = User.objects.select_related("perfil").get(id=outro_id)
            if outro_user.perfil.foto_perfil:
                outro_foto = outro_user.perfil.foto_perfil.url
            else:
                outro_foto = None
        except (User.DoesNotExist, AttributeError):
            outro_foto = None

        if outro_id not in conversas or m["ultima_data"] > conversas[outro_id]["ultima_data"]:
            conversas[outro_id] = {
                "outro_id": outro_id,
                "outro_username": outro_username,
                "outro_foto": outro_foto,
                "total": m["total"],
                "nao_lidas": m["nao_lidas"],
                "ultima_data": m["ultima_data"],
            }

    return list(conversas.values())

    from io import BytesIO
    from xhtml2pdf import pisa    
    """Gera PDF a partir de HTML usando xhtml2pdf e retorna BytesIO"""
    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html_string, dest=result, link_callback=None)
    if pisa_status.err:
        raise Exception("Erro ao gerar PDF")
    result.seek(0)
    return result