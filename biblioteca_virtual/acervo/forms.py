# acervo/forms.py

from django import forms
from .models import Livro, Emprestimo, Leitor
from django.contrib.auth.forms import AuthenticationForm


# NOVO FORMULÁRIO DE LOGIN CUSTOMIZADO
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control form-control-custom', 'placeholder': 'Username'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control form-control-custom', 'placeholder': 'Password'}
        )

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'editora', 'ano_publicacao', 'isbn']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'editora': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_publicacao': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['livro', 'leitor', 'data_devolucao_prevista']
        widgets = {
            'data_devolucao_prevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'livro': forms.Select(attrs={'class': 'form-control select2'}), # Adicionamos form-control
            'leitor': forms.Select(attrs={'class': 'form-control select2'}), # Adicionamos form-control
        }
        
        
class LeitorForm(forms.ModelForm):
    class Meta:
        model = Leitor
        fields = ['nome', 'matricula', 'turma', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'turma': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
        }