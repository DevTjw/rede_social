from django.contrib import admin
from .models import Mensagem, TemplateMensagem

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['remetente', 'destinatario', 'conteudo', 'data_envio', 'lida']
    list_filter = ['data_envio', 'lida']
    search_fields = ['remetente__username', 'destinatario__username', 'conteudo']

@admin.register(TemplateMensagem)
class TemplateMensagemAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "criado_em", "atualizado_em")
    search_fields = ("nome", "tipo")