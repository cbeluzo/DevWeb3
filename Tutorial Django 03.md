# 🧭 Tutorial 1.3 — CRUD Completo e Relacionamentos Avançados no Django


## 🎯 Objetivo do Tutorial

Neste módulo, você vai aprender a **manipular dados do sistema de forma completa** — criando, visualizando, atualizando e excluindo registros.
Essas quatro operações formam o chamado **ciclo CRUD (Create, Read, Update, Delete)**.

Também veremos como o Django simplifica essa lógica com **formulários automáticos (ModelForms)**, **views baseadas em classes (CBVs)** e **relacionamentos entre tabelas**, mantendo a separação clara entre as camadas da aplicação (modelo, visualização e template).

---

## 🧩 1. O que é CRUD?

Em qualquer sistema que armazena dados, as quatro operações básicas são sempre necessárias:

| Operação | Significado            | Exemplo prático                       |
| -------- | ---------------------- | ------------------------------------- |
| Create   | Criar um novo registro | Cadastrar um novo projeto             |
| Read     | Ler/visualizar dados   | Listar todos os projetos cadastrados  |
| Update   | Atualizar dados        | Editar o nome ou a data de um projeto |
| Delete   | Excluir dados          | Apagar um projeto antigo              |

Essas ações são implementadas no Django por meio do **ORM (Object-Relational Mapper)**, que traduz as operações em código Python para comandos SQL sem que precisemos escrever SQL manualmente.

---

## 🧱 2. Revisando os Modelos

Certifique-se de que o arquivo `projetos/models.py` contém as definições abaixo:

```python
# projetos/models.py
from django.db import models
from django.contrib.auth.models import User

# ============================
# MODELO: PROJETO
# ============================
# Representa um projeto cadastrado no sistema.
# Cada projeto pertence a um usuário (responsável).
class Projeto(models.Model):
    nome = models.CharField(max_length=100)  # campo de texto curto
    descricao = models.TextField()           # campo de texto longo
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projetos")

    def __str__(self):
        return self.nome


# ============================
# MODELO: TAREFA
# ============================
# Representa uma tarefa associada a um projeto.
class Tarefa(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    prazo = models.DateField(null=True, blank=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
```

**Explicações didáticas:**

* `ForeignKey(Projeto)` indica que **cada tarefa pertence a um projeto** (relação 1:N).
* O `related_name="tarefas"` permite acessar todas as tarefas de um projeto com `projeto.tarefas.all()`.
* O método `__str__` define como o objeto será exibido (por exemplo, em listas ou no painel administrativo).

Depois de revisar, rode:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧾 3. Criando formulários automáticos (ModelForms)

Em vez de criar formulários HTML manualmente, o Django pode **gerar formulários automaticamente** a partir dos modelos, mantendo consistência entre os dados e as regras de validação.

Crie (ou edite) o arquivo `projetos/forms.py`:

```python
# projetos/forms.py
from django import forms
from .models import Projeto, Tarefa

# ============================
# FORMULÁRIO: PROJETO
# ============================
class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ["nome", "descricao", "data_inicio", "data_fim", "responsavel"]


# ============================
# FORMULÁRIO: TAREFA
# ============================
class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ["projeto", "titulo", "descricao", "prazo", "concluida"]
```

**Explicação didática:**

* `ModelForm` lê as informações do modelo e cria automaticamente os campos correspondentes.
* O Django também usa as definições dos campos (ex: `CharField`, `DateField`) para gerar o tipo de entrada correto no HTML.

---

## ⚙️ 4. Views baseadas em classes (CBVs)

Até aqui usamos *views baseadas em função* (FBVs). Elas são simples, mas podem gerar repetição de código.
Agora usaremos *Class-Based Views (CBVs)*, que encapsulam o comportamento comum em classes genéricas.

Edite o arquivo `projetos/views.py`:

```python
# projetos/views.py

# ============================
# IMPORTAÇÕES
# ============================
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Projeto
from .forms import ProjetoForm

# ============================
# LISTAGEM DE PROJETOS
# ============================
class ProjetoListView(LoginRequiredMixin, ListView):
    model = Projeto
    template_name = "projetos/projeto_list.html"
    context_object_name = "projetos"
    # O ListView automaticamente busca todos os objetos do modelo definido.
    # O LoginRequiredMixin exige que o usuário esteja logado.


# ============================
# CRIAÇÃO DE NOVO PROJETO
# ============================
class ProjetoCreateView(LoginRequiredMixin, CreateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/projeto_form.html"
    success_url = reverse_lazy("projeto_list")
    # reverse_lazy() é usado em CBVs para evitar dependências de URL durante a importação.


# ============================
# EDIÇÃO DE PROJETO EXISTENTE
# ============================
class ProjetoUpdateView(LoginRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = "projetos/projeto_form.html"
    success_url = reverse_lazy("projeto_list")
    # O UpdateView busca automaticamente o objeto a partir do ID na URL.


# ============================
# EXCLUSÃO DE PROJETO
# ============================
class ProjetoDeleteView(LoginRequiredMixin, DeleteView):
    model = Projeto
    template_name = "projetos/projeto_confirm_delete.html"
    success_url = reverse_lazy("projeto_list")
```

**Explicação didática:**

* As *CBVs* já têm comportamento padrão para GET e POST.
* O Django injeta automaticamente um objeto `form` no contexto do template.
* `LoginRequiredMixin` força autenticação: se o usuário não estiver logado, será redirecionado para `/login/`.

---

## 🌐 5. Configurando as rotas

Atualize o arquivo `projetos/urls.py`:

```python
# projetos/urls.py
from django.urls import path
from .views import (
    ProjetoListView, ProjetoCreateView, ProjetoUpdateView, ProjetoDeleteView
)

urlpatterns = [
    path("projetos/", ProjetoListView.as_view(), name="projeto_list"),
    path("projetos/novo/", ProjetoCreateView.as_view(), name="projeto_create"),
    path("projetos/<int:pk>/editar/", ProjetoUpdateView.as_view(), name="projeto_update"),
    path("projetos/<int:pk>/excluir/", ProjetoDeleteView.as_view(), name="projeto_delete"),
]
```

---

## 🖼️ 6. Criando os templates

Crie a pasta `projetos/templates/projetos/` (se ainda não existir) e adicione os arquivos abaixo.

---

### 🗂️ 6.1. `projeto_list.html` — listagem

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Lista de Projetos</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">

  <h2 class="mb-4">Projetos</h2>

  <a href="{% url 'projeto_create' %}" class="btn btn-success mb-3">+ Novo Projeto</a>

  <table class="table table-striped">
    <thead>
      <tr>
        <th>Nome</th>
        <th>Responsável</th>
        <th>Início</th>
        <th>Fim</th>
        <th>Ações</th>
      </tr>
    </thead>
    <tbody>
      {% for projeto in projetos %}
        <tr>
          <td>{{ projeto.nome }}</td>
          <td>{{ projeto.responsavel.username }}</td>
          <td>{{ projeto.data_inicio }}</td>
          <td>{{ projeto.data_fim|default:"—" }}</td>
          <td>
            <a href="{% url 'projeto_update' projeto.pk %}" class="btn btn-warning btn-sm">Editar</a>
            <a href="{% url 'projeto_delete' projeto.pk %}" class="btn btn-danger btn-sm">Excluir</a>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="5" class="text-muted">Nenhum projeto encontrado.</td></tr>
      {% endfor %}
    </tbody>
  </table>

</body>
</html>
```

---

### 📝 6.2. `projeto_form.html` — criação/edição

```html
{% load crispy_forms_tags %}
<!--
  A tag 'load' carrega as *template tags* do pacote 'django-crispy-forms'.
  Essas tags permitem usar 'form|crispy' para renderizar o formulário com
  classes CSS do Bootstrap automaticamente.
-->

<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Formulário de Projeto</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">

  <h2 class="mb-3">
    {% if view.object %}
      Editar Projeto: {{ view.object.nome }}
    {% else %}
      Novo Projeto
    {% endif %}
  </h2>

  <!-- O formulário é enviado via POST -->
  <form method="POST">
    {% csrf_token %}
    <!-- 'csrf_token' cria um token de segurança obrigatório em formulários POST -->
    
    {{ form|crispy }}
    <!-- Renderiza todos os campos automaticamente com layout Bootstrap -->

    <button type="submit" class="btn btn-success mt-2">Salvar</button>
    <a href="{% url 'projeto_list' %}" class="btn btn-secondary mt-2">Cancelar</a>
  </form>

</body>
</html>
```

---

### ⚠️ 6.3. `projeto_confirm_delete.html` — exclusão

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Excluir Projeto</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">

  <h3>Tem certeza de que deseja excluir o projeto "{{ object.nome }}"?</h3>

  <form method="POST">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Sim, excluir</button>
    <a href="{% url 'projeto_list' %}" class="btn btn-secondary">Cancelar</a>
  </form>

</body>
</html>
```

---

## 🔗 7. Relacionando Projetos e Tarefas (1:N)

Cada projeto pode conter várias tarefas.
Vamos criar uma página que exiba todas as tarefas associadas a um projeto e permita cadastrar novas.

### 7.1. View para tarefas

Adicione ao final de `views.py`:

```python
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TarefaForm

def tarefas_do_projeto(request, projeto_id):
    # Busca o projeto pelo ID
    projeto = get_object_or_404(Projeto, pk=projeto_id)
    tarefas = projeto.tarefas.all()  # Acesso via related_name="tarefas"

    # Se o formulário foi enviado
    if request.method == "POST":
        form = TarefaForm(request.POST)
        if form.is_valid():
            form.save()  # Salva a nova tarefa
            return redirect("tarefas_projeto", projeto_id=projeto.id)
    else:
        # Cria o formulário já com o projeto pré-selecionado
        form = TarefaForm(initial={"projeto": projeto})

    return render(request, "projetos/tarefas_projeto.html", {
        "projeto": projeto,
        "tarefas": tarefas,
        "form": form
    })
```

---

### 7.2. Template de tarefas (`tarefas_projeto.html`)

```html
{% load crispy_forms_tags %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Tarefas do Projeto</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">

  <h3 class="mb-3">Tarefas de {{ projeto.nome }}</h3>

  <form method="POST" class="mb-3">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit" class="btn btn-primary">Adicionar Tarefa</button>
  </form>

  <ul class="list-group">
    {% for tarefa in tarefas %}
      <li class="list-group-item d-flex justify-content-between align-items-center">
        {{ tarefa.titulo }}
        {% if tarefa.concluida %}
          <span class="badge bg-success">Concluída</span>
        {% else %}
          <span class="badge bg-secondary">Pendente</span>
        {% endif %}
      </li>
    {% empty %}
      <li class="list-group-item text-muted">Nenhuma tarefa cadastrada.</li>
    {% endfor %}
  </ul>

  <a href="{% url 'projeto_list' %}" class="btn btn-link mt-3">Voltar à lista de projetos</a>

</body>
</html>
```

---

### 7.3. Rota das tarefas

Em `urls.py`:

```python
from .views import tarefas_do_projeto

urlpatterns += [
    path("projeto/<int:projeto_id>/tarefas/", tarefas_do_projeto, name="tarefas_projeto"),
]
```

---

## 🧠 8. Revisão Conceitual

| Conceito         | Função no Django                          | Exemplo neste tutorial           |
| ---------------- | ----------------------------------------- | -------------------------------- |
| **Model**        | Define estrutura dos dados                | `Projeto`, `Tarefa`              |
| **ModelForm**    | Gera formulários automaticamente          | `ProjetoForm`, `TarefaForm`      |
| **View (CBV)**   | Controla a lógica da página               | `CreateView`, `UpdateView`, etc. |
| **Template**     | Define o layout HTML                      | `projeto_form.html`, etc.        |
| **Template Tag** | Extensão de lógica no HTML                | `{% load crispy_forms_tags %}`   |
| **Mixin**        | Adiciona comportamento extra a uma classe | `LoginRequiredMixin`             |

---

## 🚀 Encerramento

Neste tutorial, você:

* Implementou o CRUD completo de **Projetos** com CBVs;
* Aprendeu a **renderizar formulários dinamicamente** com `crispy-forms`;
* Entendeu o papel das **template tags** e **tokens CSRF**;
* Criou o relacionamento **1:N** entre Projetos e Tarefas;
* E organizou o projeto com boa separação entre camadas (MVC).
