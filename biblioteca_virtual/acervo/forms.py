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
            'data_devolucao_prevista': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        # Chama o construtor original
        super().__init__(*args, **kwargs)
        
        # Filtra o campo 'livro' para mostrar apenas os que estão disponíveis (já existia)
        self.fields['livro'].queryset = Livro.objects.filter(disponivel=True).order_by('titulo')
        
        # ADICIONE ESTA LINHA PARA FILTRAR OS LEITORES
        # Filtra o campo 'leitor' para mostrar apenas os que estão ativos
        self.fields['leitor'].queryset = Leitor.objects.filter(ativo=True).order_by('nome')
        
        
class LeitorForm(forms.ModelForm):
    class Meta:
        model = Leitor
        fields = ['nome', 'matricula', 'turma', 'telefone']