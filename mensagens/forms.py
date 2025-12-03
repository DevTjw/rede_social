from django import forms
from .models import Mensagem
from django.contrib.auth.models import User

class MensagemForm(forms.ModelForm):
    destinatario = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Mensagem
        fields = ['destinatario', 'conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'rows': 4,  
                'class': 'form-control',
                'placeholder': 'Digite sua mensagem...',
            }),
        }

    def clean_destinatario(self):
        username = self.cleaned_data['destinatario']
        try:
            usuario = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Usuário destinatário não existe.")
        return usuario

    def save(self, commit=True):
        msg = super().save(commit=False)
        msg.destinatario = self.cleaned_data['destinatario']  # já é User
        if commit:
            msg.save()
        return msg