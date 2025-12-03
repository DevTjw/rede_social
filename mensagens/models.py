from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Mensagem(models.Model):
    remetente = models.ForeignKey(
        User,
        related_name='mensagens_enviadas',
        on_delete=models.CASCADE
    )
    destinatario = models.ForeignKey(
        User,
        related_name='mensagens_recebidas',
        on_delete=models.CASCADE
    )
    conteudo = models.TextField(max_length=1000)
    data_envio = models.DateTimeField(default=timezone.now)
    editado = models.BooleanField(default=False)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_envio']

    def __str__(self):
        return f"Mensagem de {self.remetente} para {self.destinatario}"
    
#==============================================================================================================
class TemplateMensagem(models.Model):
    TIPO_CHOICES = [
        ("confirmacao", "Confirmação de agendamento"),
        ("lembrete", "Lembrete de atendimento"),
        ("avaliacao", "Solicitação de avaliação"),
        ("pagamento", "Pagamento pendente"),
        ("personalizado", "Personalizado"),
    ]

    nome = models.CharField(max_length=100, help_text="Nome do template")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    conteudo = models.TextField(help_text="Mensagem com placeholders, ex: {cliente}, {profissional}, {data}, {hora}")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

#==============================================================================================================
