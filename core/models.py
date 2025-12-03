from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver

def caminho_foto_perfil(instance, filename):
    username = slugify(instance.usuario.username)
    user_id = instance.usuario.id
    nome_arquivo = os.path.basename(filename)  # mantém nome original
    return f"perfis/{username}_{user_id}/{nome_arquivo}"

def caminho_imagem_post(instance, filename):
    username = slugify(instance.autor.username)
    user_id = instance.autor.id
    extensao = filename.split('.')[-1]
    nome_arquivo = filename if filename else f"post.{extensao}"
    return f"posts/{username}_{user_id}/{nome_arquivo}"

class Post(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.TextField(max_length=1000)
    imagem = models.ImageField(upload_to=caminho_imagem_post, blank=True, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    curtidas = models.ManyToManyField(User, related_name='curtidas', blank=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Post de {self.autor.username} - {self.data_criacao}"

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(max_length=500)
    data_criacao = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['data_criacao']

    def __str__(self):
        return f"Comentário de {self.autor.username}"

@receiver(post_delete, sender=Post)
def deletar_imagem_post(sender, instance, **kwargs):
    if instance.imagem and instance.imagem.storage.exists(instance.imagem.name):
        instance.imagem.delete(save=False)
