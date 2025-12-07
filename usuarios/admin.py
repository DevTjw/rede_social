from django.contrib import admin
from django.utils.timezone import localtime
from .models import Perfil, Seguimento
from django.contrib import admin
from django.contrib.auth.models import User
from usuarios.views_admin import reenviar_email_confirmacao

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

@admin.action(description="Ativar usuários selecionados")
def ativar_usuarios(modeladmin, request, queryset):
    queryset.update(is_active=True)
    modeladmin.message_user(request, "Usuários ativados com sucesso!")


@admin.action(description="Inativar usuários selecionados")
def inativar_usuarios(modeladmin, request, queryset):
    queryset.update(is_active=False)
    modeladmin.message_user(request, "Usuários inativados com sucesso!")


@admin.action(description="Reenviar email de confirmação")
def reenviar_email(modeladmin, request, queryset):
    enviados = 0
    for user in queryset:
        if not user.is_active:  # evita enviar email para quem já está ativo
            reenviar_email_confirmacao(request, user)
            enviados += 1

    modeladmin.message_user(request, f"E-mails reenviados: {enviados}")


class UserAdminCustom(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined")
    search_fields = ("username", "email")

    # AÇÕES PERSONALIZADAS
    actions = [
        ativar_usuarios,
        inativar_usuarios,
        reenviar_email
    ]


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
