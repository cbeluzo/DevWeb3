# projetos/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Projeto
from .forms import ProjetoForm, TarefaForm

def login_view(request):
    # Se o formulário foi enviado (método POST)
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "projetos/login.html", {"error": "Credenciais inválidas."})
    # Se for apenas GET (primeira visita), mostra o formulário
    return render(request, "projetos/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def index(request):
    projetos = Projeto.objects.all()
    # Usamos 'projetos/index.html' (com namespace)
    return render(request, "projetos/index.html", {"projetos": projetos})

@login_required
def projeto_detalhe(request, projeto_id):
    # Busca o projeto pelo ID ou retorna erro 404 se não existir
    projeto = get_object_or_404(Projeto, pk=projeto_id)
    # Acessa as tarefas relacionadas (graças ao related_name="tarefas" definido no modelo)
    tarefas = projeto.tarefas.all()
    return render(request, "projetos/projeto_detalhe.html", {
        "projeto": projeto,
        "tarefas": tarefas
    })

@login_required
def novo_projeto(request):
    if request.method == "POST":
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = ProjetoForm()
    return render(request, "projetos/novo_projeto.html", {"form": form})

@login_required
def nova_tarefa(request):
    if request.method == "POST":
        form = TarefaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = TarefaForm()
    return render(request, "projetos/nova_tarefa.html", {"form": form})