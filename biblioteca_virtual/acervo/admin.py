# acervo/admin.py

from django.contrib import admin
from .models import Livro, Emprestimo

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'disponivel')
    list_filter = ('disponivel', 'autor')
    search_fields = ('titulo', 'autor', 'isbn')

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'leitor', 'data_emprestimo', 'data_devolucao_prevista', 'data_devolucao_real')
    list_filter = ('data_emprestimo', 'data_devolucao_prevista')
    search_fields = ('livro__titulo', 'leitor')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.bibliotecario = request.user
        super().save_model(request, obj, form, change)