# acervo/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Livro, Emprestimo, Leitor
from .forms import LivroForm, EmprestimoForm, LeitorForm
from django.utils import timezone # Importe o timezone

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator

from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.db.models import Q


        
# --------------- Registrar novo bibliotecario ------------

def home(request):
    return render(request, 'acervo/home.html')

class RegistrarBibliotecario(CreateView):
    # Usa o formulário de criação de usuário do Django
    form_class = UserCreationForm
    # Redireciona para a página de login após o registro bem-sucedido
    success_url = reverse_lazy('login')
    # Template que será usado para renderizar a página
    template_name = 'acervo/registrar.html'

    def form_valid(self, form):
        # Adiciona uma mensagem de sucesso antes de redirecionar
        messages.success(self.request, "Bibliotecário registrado com sucesso! Faça o login para continuar.")
        return super().form_valid(form)

# --------------- View para listar todos os livros ------------

def lista_livros(request):
    # A lógica de busca e filtro continua exatamente a mesma
    queryset = Livro.objects.all().order_by('titulo')
    termo_busca = request.GET.get('q')
    if termo_busca:
        queryset = queryset.filter(
            Q(titulo__icontains=termo_busca) | Q(autor__icontains=termo_busca)
        )
    filtro_status = request.GET.get('status')
    if filtro_status == 'disponivel':
        queryset = queryset.filter(disponivel=True)
    elif filtro_status == 'emprestado':
        queryset = queryset.filter(disponivel=False)

    # --- INÍCIO DA LÓGICA DE PAGINAÇÃO ---
    # 1. Cria o objeto Paginator, definindo 10 livros por página
    paginator = Paginator(queryset, 10) 

    # 2. Pega o número da página da URL (ex: /?page=2)
    page_number = request.GET.get('page')

    # 3. Pega o objeto da página correta
    page_obj = paginator.get_page(page_number)
    # --- FIM DA LÓGICA DE PAGINAÇÃO ---

    context = {
        # 4. Envia o objeto da página para o template em vez da lista inteira
        'page_obj': page_obj 
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

@login_required
def lista_emprestimos(request):
    # A lógica de busca e filtro continua exatamente a mesma
    queryset = Emprestimo.objects.select_related('livro', 'leitor').order_by('-data_emprestimo')
    termo_busca = request.GET.get('q')
    if termo_busca:
        queryset = queryset.filter(
            Q(livro__titulo__icontains=termo_busca) |
            Q(leitor__nome__icontains=termo_busca) |
            Q(leitor__matricula__icontains=termo_busca)
        )
    filtro_status = request.GET.get('status')
    if filtro_status == 'pendente':
        queryset = queryset.filter(data_devolucao_real__isnull=True)
    elif filtro_status == 'devolvido':
        queryset = queryset.filter(data_devolucao_real__isnull=False)

    # --- INÍCIO DA LÓGICA DE PAGINAÇÃO ---
    # 1. Cria o objeto Paginator, definindo 10 empréstimos por página
    paginator = Paginator(queryset, 10)

    # 2. Pega o número da página da URL
    page_number = request.GET.get('page')

    # 3. Pega o objeto da página correta
    page_obj = paginator.get_page(page_number)
    # --- FIM DA LÓGICA DE PAGINAÇÃO ---

    context = {
        # 4. Envia o objeto da página para o template
        'page_obj': page_obj
    }
    return render(request, 'acervo/lista_emprestimos.html', context)

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

@login_required
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
    
    
    
# ------------------- CRUD PARA LEITORES -----------------

class ListaLeitores(LoginRequiredMixin, ListView):
    model = Leitor
    template_name = 'acervo/lista_leitores.html'
    context_object_name = 'leitores'
    paginate_by = 10 

    # SUBSTITUA ESTE MÉTODO PELO CÓDIGO ABAIXO
    def get_queryset(self):
        # Começa com todos os leitores
        queryset = Leitor.objects.all().order_by('nome')

        # --- Lógica da Busca (continua igual) ---
        termo_busca = self.request.GET.get('q')
        if termo_busca:
            queryset = queryset.filter(
                Q(nome__icontains=termo_busca) |
                Q(matricula__icontains=termo_busca) |
                Q(turma__icontains=termo_busca)
            )

        # --- Lógica do Filtro de Status CORRIGIDA ---
        filtro_status = self.request.GET.get('status')
        if filtro_status == 'inativo':
            # Se o filtro for 'inativo', mostra apenas os inativos
            queryset = queryset.filter(ativo=False)
        else:
            # PARA QUALQUER OUTRO CASO (filtro 'ativo' ou nenhum filtro),
            # mostra apenas os leitores ATIVOS. Este é o novo padrão.
            queryset = queryset.filter(ativo=True)
            
        return queryset

class AdicionarLeitor(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Leitor
    form_class = LeitorForm
    template_name = 'acervo/adicionar_leitor.html'
    success_url = reverse_lazy('lista_leitores')
    success_message = "Leitor '%(nome)s' cadastrado com sucesso!"

class EditarLeitor(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Leitor
    form_class = LeitorForm
    template_name = 'acervo/editar_leitor.html'
    success_url = reverse_lazy('lista_leitores')
    success_message = "Leitor '%(nome)s' atualizado com sucesso!"
    
    

class InativarLeitor(LoginRequiredMixin, DeleteView):
    model = Leitor
    template_name = 'acervo/inativar_leitor_confirm.html'
    success_url = reverse_lazy('lista_leitores')

    # Este método continua correto e é usado para exibir a página (GET)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emprestimos_pendentes'] = Emprestimo.objects.filter(
            leitor=self.get_object(), 
            data_devolucao_real__isnull=True
        )
        return context

    # A correção está neste método, que lida com a ação de inativar (POST)
    def post(self, request, *args, **kwargs):
        leitor = self.get_object()
        
        # CORREÇÃO: Fazemos a consulta diretamente aqui, em vez de chamar get_context_data
        emprestimos_pendentes = Emprestimo.objects.filter(
            leitor=leitor, 
            data_devolucao_real__isnull=True
        )

        if emprestimos_pendentes.exists():
            messages.error(request, f"Não é possível inativar o leitor '{leitor.nome}', pois ele possui empréstimos pendentes.")
            return HttpResponseRedirect(self.success_url)

        # Se não houver pendências, inativa o leitor
        leitor.ativo = False
        leitor.save()
        messages.success(request, f"O leitor '{leitor.nome}' foi inativado com sucesso!")
        return HttpResponseRedirect(self.success_url)
    

# --------------- API PARA BUSCAR LIVROS DISPONÍVEIS -----------------

@login_required
def search_livros(request):
    term = request.GET.get('term', '')

    # A correção está na lógica do .filter()
    livros = Livro.objects.filter(disponivel=True).filter(
        Q(titulo__icontains=term) | Q(isbn__icontains=term)
    ).order_by('titulo')[:10]

    results = [
        {'id': livro.id, 'text': f'{livro.titulo} (ISBN: {livro.isbn})'} 
        for livro in livros
    ]
    return JsonResponse(results, safe=False)

# API PARA BUSCAR LEITORES ATIVOS
@login_required
def search_leitores(request):
    term = request.GET.get('term', '')
    # Busca por leitores ativos cujo nome ou matrícula contenha o termo
    leitores = Leitor.objects.filter(
        ativo=True
    ).filter(
        Q(nome__icontains=term) | Q(matricula__icontains=term)
    ).order_by('nome')[:10] # Limita a 10 resultados

    results = [
        {'id': leitor.id, 'text': f'{leitor.nome} (Matrícula: {leitor.matricula})'} 
        for leitor in leitores
    ]
    return JsonResponse(results, safe=False)

class ContatoView(TemplateView):
    template_name = 'acervo/contato.html'
    
class SobreNosView(TemplateView):
    template_name = 'acervo/sobre_nos.html'