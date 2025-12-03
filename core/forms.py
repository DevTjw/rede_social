from django import forms
from .models import Post, Comentario


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['conteudo', 'imagem']
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'O que está acontecendo?',
                'rows': 3
            }),
            'imagem': forms.FileInput(attrs={'class': 'form-control'})
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva um comentário...',
                'rows': 2
            })
        }
