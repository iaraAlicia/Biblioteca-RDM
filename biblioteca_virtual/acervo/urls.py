# acervo/urls.py

from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='acervo/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    # Nossa view personalizada para registrar um novo bibliotecário
    path('registrar/', views.RegistrarBibliotecario.as_view(), name='registrar'),
    
    # URLs para Livros
    path('livros/', views.lista_livros, name='lista_livros'),
    path('livros/novo/', views.adicionar_livro, name='adicionar_livro'),
    path('livros/<int:pk>/', views.detalhes_livro, name='detalhes_livro'),
    # CRUD de Livros
    path('livros/<int:pk>/editar/', views.EditarLivro.as_view(), name='editar_livro'),
    path('livros/<int:pk>/excluir/', views.ExcluirLivro.as_view(), name='excluir_livro'),
    
    # URLs para Leitores
    path('leitores/', views.ListaLeitores.as_view(), name='lista_leitores'),
    path('leitores/novo/', views.AdicionarLeitor.as_view(), name='adicionar_leitor'),
    path('leitores/<int:pk>/editar/', views.EditarLeitor.as_view(), name='editar_leitor'),
    path('leitores/<int:pk>/inativar/', views.InativarLeitor.as_view(), name='inativar_leitor'),

    # URLs para Empréstimos
    path('emprestimos/', views.lista_emprestimos, name='lista_emprestimos'),
    path('emprestimos/novo/', views.adicionar_emprestimo, name='adicionar_emprestimo'),
    
    # URLs para devolução
    path('emprestimos/<int:emprestimo_id>/devolver/', views.devolver_livro, name='devolver_livro'),
    
    # URLs de API para a busca com Select2
    path('api/search-livros/', views.search_livros, name='search_livros'),
    path('api/search-leitores/', views.search_leitores, name='search_leitores'),
    

]