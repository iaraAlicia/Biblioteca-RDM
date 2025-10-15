# acervo/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Livro, Emprestimo
from .forms import LivroForm, EmprestimoForm
from django.utils import timezone # Importe o timezone

from django.views.generic import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


from django.db.models import Q

# --------------- View para listar todos os livros ------------

def lista_livros(request):
    # Começa com todos os livros, ordenados por título
    queryset = Livro.objects.all().order_by('titulo')

    # --- Lógica da Busca ---
    termo_busca = request.GET.get('q')
    if termo_busca:
        # Usamos Q objects para fazer uma busca "OU" (OR) em múltiplos campos
        queryset = queryset.filter(
            Q(titulo__icontains=termo_busca) | Q(autor__icontains=termo_busca)
        )

    # --- Lógica do Filtro de Status ---
    filtro_status = request.GET.get('status')
    if filtro_status == 'disponivel':
        queryset = queryset.filter(disponivel=True)
    elif filtro_status == 'emprestado':
        queryset = queryset.filter(disponivel=False)

    context = {
        'livros': queryset
    }
    return render(request, 'acervo/lista_livros.html', context)




# --------------- View para adicionar um novo livro --------------
@login_required
def adicionar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            livro = form.save()
            messages.success(request, f'O livro "{livro.titulo}" foi cadastrado com sucesso!')
            return redirect('lista_livros')
    else:
        form = LivroForm()
    return render(request, 'acervo/adicionar_livro.html', {'form': form})

# -------------------- View para listar todos os empréstimos -----------------

def lista_emprestimos(request):
    emprestimos = Emprestimo.objects.all().order_by('-data_emprestimo')
    return render(request, 'acervo/lista_emprestimos.html', {'emprestimos': emprestimos})

# --------------------- View para adicionar um novo empréstimo ------------------
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

            messages.success(request, f'O empréstimo do livro "{livro_emprestado.titulo}" foi registrado com sucesso!')
            return redirect('lista_emprestimos')
    else:
        form = EmprestimoForm()
    return render(request, 'acervo/adicionar_emprestimo.html', {'form': form})


# --------------------- NOVA VIEW PARA DEVOLUÇÃO: -------------------------
@login_required
def devolver_livro(request, emprestimo_id):
    # Encontra o empréstimo específico, ou retorna um erro 404 se não existir
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)

    # Define a data de devolução real como a data e hora atuais
    emprestimo.data_devolucao_real = timezone.now().date()
    emprestimo.save()

    # Pega o livro associado ao empréstimo e o torna disponível novamente
    livro = emprestimo.livro
    livro.disponivel = True
    livro.save()
    
    # Adiciona uma mensagem de sucesso para dar feedback ao usuário
    from django.contrib import messages
    messages.success(request, f'O livro "{livro.titulo}" foi devolvido com sucesso!')

    # Redireciona o usuário de volta para a lista de empréstimos
    return redirect('lista_emprestimos')


# ------------------ DETALHES DO LIVRO, E HISTORICO DE MOVIMENTAÇÃO: ---------------

def detalhes_livro(request, pk):
    # Busca o livro específico pelo seu ID (pk), ou retorna erro 404 se não encontrar
    livro = get_object_or_404(Livro, pk=pk)
    
    # Busca todos os empréstimos associados a este livro
    # O .order_by('-data_emprestimo') mostra os mais recentes primeiro
    emprestimos = Emprestimo.objects.filter(livro=livro).order_by('-data_emprestimo')
    
    # Monta o "contexto" que será enviado para o template
    context = {
        'livro': livro,
        'emprestimos': emprestimos
    }
    
    # Renderiza o template, passando o contexto com os dados
    return render(request, 'acervo/detalhes_livro.html', context)



# ----------------- NOVAS VIEWS BASEADAS EM CLASSE: -------------------

class EditarLivro(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Livro
    form_class = LivroForm
    template_name = 'acervo/editar_livro.html'
    success_url = reverse_lazy('lista_livros') # Para onde redirecionar após o sucesso
    success_message = "O livro '%(titulo)s' foi atualizado com sucesso!"

class ExcluirLivro(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Livro
    template_name = 'acervo/excluir_livro_confirm.html'
    success_url = reverse_lazy('lista_livros')
    success_message = "O livro '%(titulo)s' foi excluído com sucesso!"
    
    def post(self, request, *args, **kwargs):
        # Pega o título do livro antes de deletá-lo
        titulo_livro = self.get_object().titulo
        # Adiciona a mensagem na fila
        messages.success(self.request, f"O livro '{titulo_livro}' foi excluído com sucesso!")
        # Continua com o processo normal de exclusão
        return self.delete(request, *args, **kwargs)