# acervo/models.py

from django.db import models
from django.contrib.auth.models import User

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editora = models.CharField(max_length=100)
    ano_publicacao = models.PositiveIntegerField()
    isbn = models.CharField(max_length=13, unique=True, help_text='13 Caracteres <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    leitor = models.CharField(max_length=100)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    bibliotecario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='emprestimos_realizados')

    def __str__(self):
        return f"{self.livro.titulo} emprestado para {self.leitor}"