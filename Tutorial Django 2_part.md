# 🧭 Tutorial 1.2 — Ampliando o Projeto Django

**Curso:** Sistemas Web em Python
**Duração sugerida:** 6 a 8 horas (2 encontros)
**Pré-requisitos:** Tutoriais 1.0 e 1.1 concluídos

---

## 🎯 Objetivo do Tutorial

Neste módulo, vamos **expandir o sistema “Gestão de Projetos”** construído anteriormente, aproximando-o de um software web real.

Até agora temos:

* uma estrutura de app funcional (`projetos`),
* modelos criados e migrados,
* e um painel básico de listagem.

Agora, iremos adicionar:

* Páginas dinâmicas (detalhes de cada projeto);
* Login e logout de usuários (autenticação completa);
* Formulários elegantes com `django-crispy-forms`;
* Migração do banco para PostgreSQL/MySQL;
* Um dashboard interativo com Plotly.

Cada passo será explicado em linguagem acessível e profissional.

---

## 🧩 1. Criando a página de detalhes de um projeto

A página inicial lista todos os projetos, mas ainda não permite visualizar detalhes de cada um. Em sistemas reais, é essencial que cada item da lista possa ser clicado para mostrar suas informações completas — e, no caso do nosso app, também as **tarefas associadas**.

---

### 1.1. Adicionando uma rota dinâmica

Uma rota dinâmica recebe **parâmetros variáveis** na URL (por exemplo, o ID do projeto).
Isso é essencial para gerar páginas personalizadas.

No arquivo `projetos/urls.py`, adicione:

```python
# projetos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # Nova rota dinâmica que recebe o ID do projeto
    path("projeto/<int:projeto_id>/", views.projeto_detalhe, name="projeto_detalhe"),
]
```

💡 **Explicação:**
`<int:projeto_id>` indica que o valor virá como número inteiro e será repassado para a view como argumento.
Assim, o caminho `/projeto/1/` acessa o projeto de ID 1.

---

### 1.2. Criando a view de detalhes

No arquivo `projetos/views.py`, adicione:

```python
# projetos/views.py
from django.shortcuts import render, get_object_or_404
from .models import Projeto

def projeto_detalhe(request, projeto_id):
    # Busca o projeto pelo ID ou retorna erro 404 se não existir
    projeto = get_object_or_404(Projeto, pk=projeto_id)
    # Acessa as tarefas relacionadas (graças ao related_name="tarefas" definido no modelo)
    tarefas = projeto.tarefas.all()
    return render(request, "projetos/projeto_detalhe.html", {
        "projeto": projeto,
        "tarefas": tarefas
    })
```

💡 **Explicação:**

* `get_object_or_404()` é uma função utilitária do Django que evita erros: se o objeto não for encontrado, mostra automaticamente uma página 404 amigável.
* `projeto.tarefas.all()` usa o relacionamento entre modelos: um projeto pode ter várias tarefas.

---

### 1.3. Criando o template de detalhes

Crie o arquivo `projetos/templates/projetos/projeto_detalhe.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>{{ projeto.nome }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">

  <h2>{{ projeto.nome }}</h2>
  <p class="text-muted">Responsável: {{ projeto.responsavel.username }}</p>
  <p>{{ projeto.descricao }}</p>

  <h4 class="mt-4">Tarefas</h4>
  <ul class="list-group">
    {% for tarefa in tarefas %}
      <li class="list-group-item d-flex justify-content-between align-items-center">
        {{ tarefa.titulo }}
        <span class="badge {% if tarefa.concluida %}text-bg-success{% else %}text-bg-secondary{% endif %}">
          {% if tarefa.concluida %}Concluída{% else %}Pendente{% endif %}
        </span>
      </li>
    {% empty %}
      <li class="list-group-item text-muted">Sem tarefas registradas.</li>
    {% endfor %}
  </ul>

  <a href="{% url 'index' %}" class="btn btn-link mt-3">Voltar</a>
</body>
</html>
```

💡 **Explicação:**
O Django interpreta variáveis e estruturas de controle (como `for` e `if`) dentro de `{% %}` e `{{ }}`.
Aqui usamos:

* `{{ projeto.nome }}` → insere dinamicamente o nome do projeto;
* `{% for tarefa in tarefas %}` → gera uma linha para cada tarefa.

---

### 1.4. Tornando os projetos clicáveis na página inicial

No arquivo `projetos/templates/projetos/index.html`, substitua os itens da lista por links:

```html
<ul class="list-group">
  {% for projeto in projetos %}
    <li class="list-group-item">
	 <a href="{% url 'projeto_detalhe' projeto.id %}" class="list-group-item list-group-item-action">
      	<strong>{{ projeto.nome }}</strong> — {{ projeto.responsavel.username }}
      </a>
    </li>
  {% empty %}
    <li class="list-group-item text-muted">Nenhum projeto cadastrado.</li>
  {% endfor %}
</ul>
```

💡 **Explicação:**
A *template tag* `{% url 'projeto_detalhe' projeto.id %}` gera automaticamente o link com base no nome da rota definida no `urls.py`.

---

## 🔐 2. Implementando autenticação (login e logout)

Sistemas reais precisam saber quem está usando o sistema. O Django já traz um **sistema completo de autenticação**, com login, logout, senhas criptografadas e controle de sessão.

---

### 2.1. Criando as views de login e logout

No arquivo `projetos/views.py`, adicione:

```python
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

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
```

💡 **Explicação:**

* `authenticate()` verifica o usuário e senha no banco.
* `login()` cria uma sessão (cookie seguro).
* `logout()` encerra a sessão.
  Essas funções já vêm integradas ao sistema de autenticação do Django.

---
