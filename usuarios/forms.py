from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil
from .models import DadosPessoais
from django import forms
from .models import DadosPagamento

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=30, required=True, label="Sobrenome")
    email1 = forms.EmailField(required=True, label="Email")
    email2 = forms.EmailField(required=True, label="Confirme o Email")

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email1",
            "email2",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email1")
        email2 = cleaned_data.get("email2")

        # 🔹 Verifica se os e-mails coincidem
        if email1 and email2 and email1 != email2:
            self.add_error("email2", "Os e-mails não coincidem. Tente novamente.")

        # 🔹 Verifica se o e-mail já está em uso
        if email1 and User.objects.filter(email=email1).exists():
            self.add_error("email1", "Este e-mail já está em uso.")

        return cleaned_data

    def clean_password2(self):
        """
        Sobrescreve a validação padrão para personalizar a mensagem de erro
        se as senhas não coincidirem.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem. Tente novamente.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email1"]
        if commit:
            user.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input',
                'placeholder': 'Usuario', 'readonly': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input',
                'placeholder': 'Email', 'readonly': True,
            }),
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['bio', 'localizacao', 'nascimento', 'foto_perfil']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control'}),
            'nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'})
        }
   
class DadosPessoaisForm(forms.ModelForm):
    class Meta:
        model = DadosPessoais
        fields = [
            "cpf",
            "telefone",
            "email_recuperacao",
            "data_nascimento",
            "rua",
            "numero_casa",
            "bairro",
            "cidade",
            "estado",
            "cep",
        ]
        widgets = {
            "cpf": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "000.000.000-00"
            }),
            "telefone": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "(00) 00000-0000"
            }),
            "email_recuperacao": forms.EmailInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "email@exemplo.com"
            }),
            "data_nascimento": forms.DateInput(format='%Y-%m-%d', attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "type": "date"
            }),
            "rua": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "Rua"
            }),
            "numero_casa": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "Número"
            }),
            "bairro": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "Bairro"
            }),
            "cidade": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "Cidade"
            }),
            "estado": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "Estado"
            }),
            "cep": forms.TextInput(attrs={
                "class": "form-control form-control-lg border-2 rounded-3 shadow-sm futuristic-input",
                "placeholder": "00000-000"
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        if not cpf:
            return cpf

        cpf_normalizado = cpf.replace(".", "").replace("-", "")
        qs = DadosPessoais.objects.filter(cpf=cpf)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Este CPF já está cadastrado em outro usuário.")

        if len(cpf_normalizado) != 11 or not cpf_normalizado.isdigit():
            raise forms.ValidationError("CPF inválido. Digite apenas números válidos.")

        return cpf

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # pega o usuário passado na view
        super().__init__(*args, **kwargs)

        # CPF readonly
        if self.instance and self.instance.cpf:
            self.fields['cpf'].widget.attrs['readonly'] = True

        # Data de nascimento: só preenche se o campo estiver vazio
        if usuario:
            from .models import Perfil
            try:
                perfil = Perfil.objects.get(usuario=usuario)
                if perfil.nascimento and not self.initial.get('data_nascimento'):
                    self.initial['data_nascimento'] = perfil.nascimento
            except Perfil.DoesNotExist:
                pass

class DadosPagamentoForm(forms.ModelForm):
    class Meta:
        model = DadosPagamento
        fields = [
            'metodo_pagamento',
            'nome_titular',
            'numero_cartao',
            'validade',
            'codigo_seguranca',
            'bandeira',
            'chave_pix',
        ]
        widgets = {
            'numero_cartao': forms.TextInput(attrs={'placeholder': '**** **** **** ****'}),
            'validade': forms.TextInput(attrs={'placeholder': 'MM/AA'}),
            'codigo_seguranca': forms.PasswordInput(render_value=True, attrs={'placeholder': 'CVV'}),
            'chave_pix': forms.TextInput(attrs={'placeholder': 'Chave Pix'}),
        }