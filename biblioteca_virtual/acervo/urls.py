# acervo/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs para Livros
    path('livros/', views.lista_livros, name='lista_livros'),
    path('livros/novo/', views.adicionar_livro, name='adicionar_livro'),
    path('livros/<int:pk>/', views.detalhes_livro, name='detalhes_livro'),
    # CRUD de Livros
    path('livros/<int:pk>/editar/', views.EditarLivro.as_view(), name='editar_livro'),
    path('livros/<int:pk>/excluir/', views.ExcluirLivro.as_view(), name='excluir_livro'),

    # URLs para Empréstimos
    path('emprestimos/', views.lista_emprestimos, name='lista_emprestimos'),
    path('emprestimos/novo/', views.adicionar_emprestimo, name='adicionar_emprestimo'),
    
     # URLs para devolução
    path('emprestimos/<int:emprestimo_id>/devolver/', views.devolver_livro, name='devolver_livro'),
    

]