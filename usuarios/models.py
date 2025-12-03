from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
from django.db.models.signals import pre_save
from django.dispatch import receiver

def caminho_foto_perfil(instance, filename):
    username = slugify(instance.usuario.username)
    user_id = instance.usuario.id
    nome_arquivo = os.path.basename(filename)
    return f"perfis/{username}_{user_id}/{nome_arquivo}"

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    bio = models.TextField(max_length=500, blank=True)
    localizacao = models.CharField(max_length=100, blank=True)
    nascimento = models.DateField(null=True, blank=True)
    foto_perfil = models.ImageField(upload_to=caminho_foto_perfil, blank=True)
    seguidores = models.ManyToManyField(User, related_name='seguindo', blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class DadosPessoais(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dados_pessoais")

    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email_recuperacao = models.CharField(max_length=100, blank=True, verbose_name="Email para recuperar conta")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    rua = models.CharField(max_length=255, blank=True, verbose_name="Rua")
    numero_casa = models.CharField(max_length=10, blank=True, verbose_name="Numero")
    bairro = models.CharField(max_length=100, blank=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=50, blank=True, verbose_name="Estado")
    cep = models.CharField(max_length=10, blank=True, verbose_name="CEP")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dados pessoais de {self.usuario.username}"

class DadosPagamento(models.Model):
    METODOS_PAGAMENTO = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'Pix'),
        ('boleto', 'Boleto Bancário'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dados_pagamento")

    metodo_pagamento = models.CharField(
        max_length=30,
        choices=METODOS_PAGAMENTO,
        default='cartao_credito',
        verbose_name="Método de Pagamento"
    )

    nome_titular = models.CharField(max_length=100, verbose_name="Nome do Titular", blank=True)
    numero_cartao = models.CharField(max_length=19, verbose_name="Número do Cartão", blank=True)
    validade = models.CharField(max_length=5, verbose_name="Validade (MM/AA)", blank=True)
    codigo_seguranca = models.CharField(max_length=4, verbose_name="CVV", blank=True)
    bandeira = models.CharField(max_length=20, blank=True, verbose_name="Bandeira do Cartão")
    chave_pix = models.CharField(max_length=200, blank=True, verbose_name="Chave Pix")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pagamento de {self.usuario.username}"

class Seguimento(models.Model):
    seguidor = models.ForeignKey(User, related_name='seguindo_users', on_delete=models.CASCADE)
    seguindo = models.ForeignKey(User, related_name='seguindo_users_2', on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguindo')

    def __str__(self):
        return f'{self.seguidor.username} segue {self.seguindo.username}'

@receiver(pre_save, sender=Perfil)
def deletar_foto_anterior(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        perfil_antigo = Perfil.objects.get(pk=instance.pk)
    except Perfil.DoesNotExist:
        return

    foto_antiga = perfil_antigo.foto_perfil
    nova_foto = instance.foto_perfil

    if foto_antiga and foto_antiga != nova_foto:
        if foto_antiga.storage.exists(foto_antiga.name):
            foto_antiga.storage.delete(foto_antiga.name)
