# acervo/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Livro, Emprestimo
from .forms import LivroForm, EmprestimoForm

# View para listar todos os livros
def lista_livros(request):
    livros = Livro.objects.all().order_by('titulo')
    return render(request, 'acervo/lista_livros.html', {'livros': livros})

# View para adicionar um novo livro
@login_required
def adicionar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_livros')
    else:
        form = LivroForm()
    return render(request, 'acervo/adicionar_livro.html', {'form': form})

# View para listar todos os empréstimos
def lista_emprestimos(request):
    emprestimos = Emprestimo.objects.all().order_by('-data_emprestimo')
    return render(request, 'acervo/lista_emprestimos.html', {'emprestimos': emprestimos})

# View para adicionar um novo empréstimo
@login_required
def adicionar_emprestimo(request):
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            # Não salva no banco de dados ainda
            emprestimo = form.save(commit=False)
            # Define o bibliotecário como o usuário logado
            emprestimo.bibliotecario = request.user
            emprestimo.save()

            # Atualiza o status do livro para indisponível
            livro_emprestado = emprestimo.livro
            livro_emprestado.disponivel = False
            livro_emprestado.save()

            return redirect('lista_emprestimos')
    else:
        form = EmprestimoForm()
    return render(request, 'acervo/adicionar_emprestimo.html', {'form': form})