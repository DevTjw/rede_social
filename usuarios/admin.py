from django.contrib import admin
from django.utils.timezone import localtime
from .models import Perfil, Seguimento

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'localizacao', 'data_criacao_formatada']
    list_filter = ['data_criacao']
    search_fields = ['usuario__username', 'localizacao']

    def data_criacao_formatada(self, obj):
        return localtime(obj.data_criacao).strftime("%d/%m/%Y %H:%M")
    data_criacao_formatada.short_description = "Data de Criação"

@admin.register(Seguimento)
class SeguimentoAdmin(admin.ModelAdmin):
    list_display = ['seguidor', 'seguindo', 'criado_em']
    list_filter = ['criado_em']
    search_fields = ['seguidor__username', 'seguindo__username']

