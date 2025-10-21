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
        # Inclua os novos campos, exceto 'copias_disponiveis'
        fields = ['titulo', 'autor', 'editora', 'ano_publicacao', 'isbn', 'genero', 'descricao', 'numero_copias']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'editora': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_publicacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'numero_copias': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # Lógica para garantir que 'copias_disponiveis' acompanhe 'numero_copias'
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk: # Se for um livro novo
            instance.copias_disponiveis = instance.numero_copias
        else: # Se estiver editando
            livro_antigo = Livro.objects.get(pk=instance.pk)
            # Ajusta cópias disponíveis pela diferença
            diferenca = instance.numero_copias - livro_antigo.numero_copias
            instance.copias_disponiveis = max(0, livro_antigo.copias_disponiveis + diferenca) # Garante que não fique negativo
            
        if commit:
            instance.save()
        return instance

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