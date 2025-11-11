# projetos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # Nova rota dinâmica que recebe o ID do projeto
    path("projeto/<int:projeto_id>/", views.projeto_detalhe, name="projeto_detalhe"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('novo_projeto/', views.novo_projeto, name='novo_projeto'),
    path('novo_tarefa/', views.nova_tarefa, name='nova_tarefa')
]