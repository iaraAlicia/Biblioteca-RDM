# acervo/forms.py

from django import forms
from .models import Livro, Emprestimo, Leitor

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'editora', 'ano_publicacao', 'isbn']
        # O campo 'disponivel' não está aqui porque por padrão, 
        # um livro novo sempre estará disponível.

class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['livro', 'leitor', 'data_devolucao_prevista']
        widgets = {
            'data_devolucao_prevista': forms.DateInput(attrs={'type': 'date'}),
            
            # Garantimos que os dois campos são do tipo Select
            # e ambos têm a classe 'select2' para o JavaScript encontrar.
            'livro': forms.Select(attrs={'class': 'select2'}),
            'leitor': forms.Select(attrs={'class': 'select2'}),
        }
        
        
class LeitorForm(forms.ModelForm):
    class Meta:
        model = Leitor
        fields = ['nome', 'matricula', 'turma', 'telefone']