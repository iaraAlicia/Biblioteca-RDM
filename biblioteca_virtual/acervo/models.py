# acervo/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.core.validators import MinValueValidator 

# ADICIONE O NOVO MODELO AQUI
class Leitor(models.Model):
    nome = models.CharField(max_length=200)
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Matrícula")
    turma = models.CharField(max_length=50, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editora = models.CharField(max_length=100)
    ano_publicacao = models.PositiveIntegerField()
    isbn = models.CharField(max_length=13, unique=True, help_text='13 Caracteres ISBN')
    genero = models.CharField(max_length=100, blank=True, verbose_name="Gênero")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    numero_copias = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(0)], 
        verbose_name="Número de Cópias Totais"
    )
    copias_disponiveis = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        verbose_name="Cópias Disponíveis"
    )

    # REMOVA O CAMPO ANTIGO 'disponivel'
    # disponivel = models.BooleanField(default=True) <-- REMOVA ESTA LINHA

    def __str__(self):
        return self.titulo

    # MÉTODO AUXILIAR (ÚTIL NO FUTURO)
    def tem_copias_disponiveis(self):
        return self.copias_disponiveis > 0

    def __str__(self):
        return self.titulo

    # MÉTODO AUXILIAR (ÚTIL NO FUTURO)
    def tem_copias_disponiveis(self):
        return self.copias_disponiveis > 0

class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    leitor = models.ForeignKey(Leitor, on_delete=models.PROTECT, related_name='emprestimos')
    data_emprestimo = models.DateField(auto_now_add=True)
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    bibliotecario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='emprestimos_realizados')

    def __str__(self):
        return f"{self.livro.titulo} emprestado para {self.leitor}"
    
    @property
    def esta_atrasado(self):
        # A condição só se aplica se o livro ainda não foi devolvido
        if self.data_devolucao_real is None:
            # Retorna True se a data de hoje for maior que a data de devolução prevista
            return timezone.now().date() > self.data_devolucao_prevista
        return False