# acervo/views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Livro, Emprestimo, Leitor
from .forms import LivroForm, EmprestimoForm, LeitorForm
from django.utils import timezone

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator

from django.http import HttpResponseRedirect,JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from weasyprint import HTML


        
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

# --------------- View para dashboard ------------

@login_required
def dashboard(request):
    # --- Cálculos dos Números Chave ---
    total_livros = Livro.objects.count()
    livros_emprestados = Emprestimo.objects.filter(data_devolucao_real__isnull=True).count()
    livros_disponiveis = total_livros - livros_emprestados # Ou Livro.objects.filter(disponivel=True).count()
    
    emprestimos_atrasados = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True,
        data_devolucao_prevista__lt=timezone.now().date()
    ).count()
    
    total_leitores_ativos = Leitor.objects.filter(ativo=True).count()

    # --- (Opcional) Buscar Atividade Recente ---
    ultimos_emprestimos = Emprestimo.objects.select_related('livro', 'leitor').order_by('-data_emprestimo')[:5] # Pega os 5 mais recentes

    context = {
        'total_livros': total_livros,
        'livros_emprestados': livros_emprestados,
        'livros_disponiveis': livros_disponiveis,
        'emprestimos_atrasados': emprestimos_atrasados,
        'total_leitores_ativos': total_leitores_ativos,
        'ultimos_emprestimos': ultimos_emprestimos,
    }
    return render(request, 'acervo/dashboard.html', context)


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
    queryset = Emprestimo.objects.select_related('livro', 'leitor').order_by('-data_emprestimo')

    # Pega todos os parâmetros da URL
    termo_busca = request.GET.get('q')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status')

    # Aplica os filtros
    if termo_busca:
        queryset = queryset.filter(
            Q(livro__titulo__icontains=termo_busca) |
            Q(leitor__nome__icontains=termo_busca) |
            Q(leitor__matricula__icontains=termo_busca)
        )
    if data_inicio:
        queryset = queryset.filter(data_emprestimo__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data_emprestimo__lte=data_fim)
    if status == 'pendente':
        queryset = queryset.filter(data_devolucao_real__isnull=True)
    elif status == 'devolvido':
        queryset = queryset.filter(data_devolucao_real__isnull=False)
    
    # Paginação (continua igual)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filtros_aplicados': request.GET # Passa os filtros para manter os valores nos campos
    }
    return render(request, 'acervo/lista_emprestimos.html', context)

# --------------------- View para adicionar um novo empréstimo ------------------
@login_required
def adicionar_emprestimo(request):
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            emprestimo = form.save(commit=False)
            
            # --- LÓGICA DE CÓPIAS ---
            livro_emprestado = emprestimo.livro
            if livro_emprestado.copias_disponiveis > 0:
                # Diminui as cópias disponíveis
                livro_emprestado.copias_disponiveis -= 1
                livro_emprestado.save()

                # Salva o empréstimo
                emprestimo.bibliotecario = request.user
                emprestimo.save()
                
                messages.success(request, f'O empréstimo do livro "{livro_emprestado.titulo}" foi registrado com sucesso!')
                return redirect('lista_emprestimos')
            else:
                messages.error(request, f'Não há cópias disponíveis do livro "{livro_emprestado.titulo}" no momento.')
                # Retorna o formulário com o erro
                return render(request, 'acervo/adicionar_emprestimo.html', {'form': form})
            # --- FIM DA LÓGICA ---
    else:
        # Filtra os livros no GET para mostrar apenas os com cópias disponíveis
        form = EmprestimoForm()
        # Ajuste no AJAX do Select2 cuidará disso dinamicamente

    return render(request, 'acervo/adicionar_emprestimo.html', {'form': form})


# --------------------- NOVA VIEW PARA DEVOLUÇÃO: -------------------------
@login_required
def devolver_livro(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)

    # Verifica se já não foi devolvido para evitar contagem dupla
    if emprestimo.data_devolucao_real is None:
        emprestimo.data_devolucao_real = timezone.now().date()
        emprestimo.save()

        livro = emprestimo.livro
        # --- LÓGICA DE CÓPIAS ---
        # Aumenta as cópias disponíveis, garantindo que não ultrapasse o total
        livro.copias_disponiveis = min(livro.numero_copias, livro.copias_disponiveis + 1)
        livro.save()
        # --- FIM DA LÓGICA ---
        
        messages.success(request, f'O livro "{livro.titulo}" foi devolvido com sucesso!')
    else:
        messages.warning(request, f'O livro "{emprestimo.livro.titulo}" já havia sido devolvido.')

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
    livros = Livro.objects.filter(
        # ALTERE AQUI: filtra por cópias disponíveis > 0
        copias_disponiveis__gt=0 
    ).filter(
        Q(titulo__icontains=term) | Q(isbn__icontains=term)
    ).order_by('titulo')[:10]

    results = [
        # ADICIONE a contagem de cópias ao texto exibido
        {'id': livro.id, 'text': f'{livro.titulo} ({livro.copias_disponiveis} cópias) - ISBN: {livro.isbn}'} 
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
    
  # A LÓGICA GERAR RELATORIO EMPRESTIMO
    
@login_required
def gerar_relatorio_emprestimos_pdf(request):
    # A LÓGICA DE FILTRO É EXATAMENTE A MESMA DA 'lista_emprestimos'
    queryset = Emprestimo.objects.select_related('livro', 'leitor').order_by('-data_emprestimo')
    termo_busca = request.GET.get('q')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status')

    if termo_busca:
        queryset = queryset.filter(Q(livro__titulo__icontains=termo_busca) | Q(leitor__nome__icontains=termo_busca) | Q(leitor__matricula__icontains=termo_busca))
    if data_inicio:
        queryset = queryset.filter(data_emprestimo__gte=data_inicio)
    if data_fim:
        queryset = queryset.filter(data_emprestimo__lte=data_fim)
    if status == 'pendente':
        queryset = queryset.filter(data_devolucao_real__isnull=True)
    elif status == 'devolvido':
        queryset = queryset.filter(data_devolucao_real__isnull=False)

    # Renderiza um template HTML com os dados filtrados
    html_string = render_to_string('acervo/partials/_relatorio_pdf.html', {'emprestimos': queryset})

    # Cria o PDF a partir do HTML
    pdf = HTML(string=html_string).write_pdf()

    # Cria a resposta HTTP para forçar o download do arquivo
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_emprestimos.pdf"'
    
    return response