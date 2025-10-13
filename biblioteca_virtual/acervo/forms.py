# acervo/forms.py

from django import forms
from .models import Livro, Emprestimo

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
            'data_devolucao_prevista': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra o campo 'livro' para mostrar apenas os que estão disponíveis.
        self.fields['livro'].queryset = Livro.objects.filter(disponivel=True)