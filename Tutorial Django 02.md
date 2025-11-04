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

### 2.2. Criando o template de login

Crie `projetos/templates/projetos/login.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Login</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">
  <div class="container" style="max-width: 420px;">
    <h2 class="mb-4">Entrar no Sistema</h2>

    {% if error %}
      <div class="alert alert-danger">{{ error }}</div>
    {% endif %}

    <form method="POST">
      {% csrf_token %}
      <!-- csrf_token previne ataques de falsificação de requisição -->
      <input class="form-control mb-2" type="text" name="username" placeholder="Usuário" required>
      <input class="form-control mb-3" type="password" name="password" placeholder="Senha" required>
      <button class="btn btn-primary w-100">Entrar</button>
    </form>
  </div>
</body>
</html>
```

---

### 2.3. Ajustando configurações de login no Django

No arquivo `gestao_projetos/settings.py`, adicione no final:

```python
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "login"
```

💡 **Explicação:**
Essas variáveis informam ao Django **qual é a página de login** e **para onde redirecionar após login/logout**.

---

### 2.4. Protegendo páginas com o decorador `login_required`

No `views.py`, importe e use:

```python
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    projetos = Projeto.objects.all()
    return render(request, "projetos/index.html", {"projetos": projetos, "user": request.user})

@login_required
def projeto_detalhe(request, projeto_id):
    projeto = get_object_or_404(Projeto, pk=projeto_id)
    tarefas = projeto.tarefas.all()
    return render(request, "projetos/projeto_detalhe.html", {"projeto": projeto, "tarefas": tarefas})
```

💡 **Explicação:**

* `@login_required` impede o acesso de usuários não autenticados.
* Se o usuário não estiver logado, é redirecionado para `LOGIN_URL`.

---

Em projetos/urls.py, incluir:

```python

# projetos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # Nova rota dinâmica que recebe o ID do projeto
    path("projeto/<int:projeto_id>/", views.projeto_detalhe, name="projeto_detalhe"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout')
]
```



No arquivo projetos/templates/projetos/index.html, logo após:

```
<body class="p-4">
    <h1 class="mb-4">Projetos Cadastrados</h1>
```

adicionar:

```
  <p>Olá, {{ user.first_name }}  {{ user.last_name }}!</p>
  <p>Seu e-mail: {{ user.email }}</p>
  {% if user.is_staff %}
    <p>Você é um administrador.</p>
  {% endif %}
```

Adicionar também ao final:

```
<a href="{% url 'logout' %}" class="list-group-item list-group-item-action">
     <strong>Sair</strong>
 </a>
</body>
</html>
```

## 🧾 3. Criando formulários elegantes com `django-crispy-forms`

Os formulários padrões do Django funcionam bem, mas são simples visualmente.
Com o `django-crispy-forms`, eles ganham aparência moderna e integração com o Bootstrap.

---

### 3.1. Configuração

Instale o pacote:

```bash
pip install crispy-bootstrap5
```

Em `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "crispy_forms",
    "crispy_bootstrap5",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

---

### 3.2. Criando o formulário e view

Em `projetos/forms.py`:

```python
from django import forms
from .models import Projeto

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ["nome", "descricao", "data_inicio", "data_fim", "responsavel"]
```

Em `views.py`:

```python
from .forms import ProjetoForm

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
```

---

### 3.3. Template com Crispy Forms

Crie `projetos/templates/projetos/novo_projeto.html`:

```html
{% load crispy_forms_tags %}
<!-- A tag acima ativa o uso das funções do crispy-forms dentro do template -->

<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Novo Projeto</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-5">

  <h2 class="mb-4">Cadastrar Novo Projeto</h2>

  <form method="POST" novalidate>
    {% csrf_token %}
    {{ form|crispy }}
    <!-- O filtro '|crispy' aplica automaticamente as classes do Bootstrap aos campos -->
    <button type="submit" class="btn btn-success">Salvar</button>
  </form>

</body>
</html>
```

---

-----

## 4\. Migrando para o banco PostgreSQL

O SQLite é ótimo para desenvolvimento, mas em produção usamos bancos mais robustos. Vou te mostrar como mudar para o PostgreSQL.

**Por que fazer isso?**
Essa mudança mostra como o Django facilita a portabilidade entre bancos, graças ao ORM. Assim, você aprende a preparar seu projeto para ambientes reais de hospedagem.

### 4.1. Instalando o PostgreSQL

No Ubuntu, rode:

```bash
sudo apt install postgresql postgresql-contrib -y
```

### 4.2. Criando o banco e usuário

Acesse o console do PostgreSQL:

```bash
sudo -u postgres psql
```

E execute os seguintes comandos SQL:

```sql
CREATE DATABASE gestao_db;
CREATE USER gestao_user WITH PASSWORD 'senha123';
ALTER ROLE gestao_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE gestao_db TO gestao_user;
\q
```

### 4.3. Configurando o Django

No Tutorial 1.0, nós já instalamos o driver `psycopg2-binary`, então não precisamos instalá-lo novamente.

Agora, basta editar `gestao_projetos/settings.py` e substituir a seção `DATABASES`:

```python
# gestao_projetos/settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "gestao_db",
        "USER": "gestao_user",
        "PASSWORD": "senha123",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### 4.4. Migrando e criando o superusuário (de novo)

Ao trocar o banco, **os dados do SQLite são perdidos**. Estamos apontando para um banco de dados novo e vazio.

Execute as migrações para criar as tabelas no PostgreSQL:

```bash
python manage.py migrate
```

Como o banco é novo, precisamos criar um superusuário novamente:

```bash
python manage.py createsuperuser
```

Pronto\! Seu sistema agora usa PostgreSQL. Nenhuma linha do código de *lógica* (views, models) precisou ser alterada — apenas as configurações.

-----

Perfeito — abaixo está a **versão equivalente do tutorial para o MySQL**, mantendo o mesmo formato e objetivo didático, adaptado ao ambiente mais comum em servidores compartilhados e aplicações web em produção.

---

## 4. Migrando para o banco MySQL

O SQLite é excelente para desenvolvimento local, mas em produção o uso de bancos mais robustos é preferível. Vamos migrar o projeto para **MySQL**, um dos bancos relacionais mais utilizados em aplicações web.

**Por que fazer isso?**
O Django possui suporte nativo ao MySQL via ORM. Essa migração mostra como adaptar o projeto para um ambiente real de hospedagem, sem alterar o código da aplicação — apenas as configurações de conexão.

---

### 4.1. Instalando o MySQL

No Ubuntu, execute:

```bash
sudo apt install mysql-server mysql-client libmysqlclient-dev -y
```

Verifique se o serviço está ativo:

```bash
sudo systemctl status mysql
```

---

### 4.2. Criando o banco e o usuário

Acesse o console do MySQL como administrador:

```bash
sudo mysql -u root -p
```

E crie o banco e o usuário específicos para o projeto:

```sql
CREATE DATABASE gestao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gestao_user'@'localhost' IDENTIFIED BY 'senha123';
GRANT ALL PRIVILEGES ON gestao_db.* TO 'gestao_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Esses comandos criam um banco com suporte a acentuação UTF-8 e concedem ao usuário acesso total apenas a esse banco.

---

### 4.3. Instalando o driver Python

O Django se conecta ao MySQL via biblioteca `mysqlclient`. Instale-a no ambiente virtual:

```bash
pip install mysqlclient
```

Se preferir compatibilidade com versões mais recentes e ambientes restritos, você pode usar o driver puro em Python:

```bash
pip install pymysql
```

E adicionar no início do arquivo `gestao_projetos/__init__.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

### 4.4. Configurando o Django

Edite o arquivo `gestao_projetos/settings.py` e substitua a seção `DATABASES` por:

```python
# gestao_projetos/settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "gestao_db",
        "USER": "gestao_user",
        "PASSWORD": "senha123",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

---

### 4.5. Migrando e criando o superusuário

Como estamos apontando para um novo banco, as tabelas ainda não existem. Execute:

```bash
python manage.py migrate
```

E recrie o superusuário:

```bash
python manage.py createsuperuser
```

---

### 4.6. Testando a conexão

Para confirmar que tudo está funcionando, rode o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Acesse o painel administrativo (`http://127.0.0.1:8000/admin/`) e autentique-se com o superusuário criado.


-----
## 5\. Criando um dashboard com Plotly

Para fechar, quero mostrar como gerar gráficos interativos usando Plotly dentro de uma página Django.

**Por que fazer isso?**
Visualizações ajudam a entender os dados e são muito valorizadas em sistemas de gestão. Aqui, você vai unir Python, consultas do ORM e HTML.

### 5.1. Instalando Plotly

No terminal, dentro do ambiente virtual:

```bash
pip install plotly
```

### 5.2. Criando a view do dashboard

Em `projetos/views.py`, adicione os imports e a nova view:

```python
# projetos/views.py

# ... (outros imports) ...
import plotly.express as px
from django.db.models import Count
from django.utils.safestring import mark_safe # Importe o mark_safe

# ... (outras views) ...

@login_required # Proteger a view
def dashboard(request):
    # Faz uma consulta no ORM contando quantas tarefas cada projeto tem
    dados = Projeto.objects.annotate(num_tarefas=Count("tarefas"))
    
    # Gera um gráfico de barras com Plotly
    fig = px.bar(
        x=[p.nome for p in dados],
        y=[p.num_tarefas for p in dados],
        labels={"x": "Projetos", "y": "Número de Tarefas"},
        title="Tarefas por Projeto"
    )
    
    # Converte o gráfico em HTML (sem incluir as tags <html> ou <body>)
    grafico_html = mark_safe(fig.to_html(full_html=False))
    
    return render(request, "projetos/dashboard.html", {"grafico_html": grafico_html})
```

O `mark_safe` é necessário para dizer ao Django que o HTML do gráfico é seguro e não deve ser "escapado".

### 5.3. Criando o template

Crie o arquivo `projetos/templates/projetos/dashboard.html`:

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
  <h2 class="mb-4">Análise de Tarefas por Projeto</h2>
  
  <div>
    {{ grafico_html|safe }}
  </div>
  
  <a href="{% url 'index' %}" class="btn btn-link mt-3">Voltar</a>
</body>
</html>
```

### 5.4. Adicionando a rota e o link

Adicione a rota em `projetos/urls.py`:

```python
# projetos/urls.py
# ...
urlpatterns += [
    # ...
    path("dashboard/", views.dashboard, name="dashboard"),
]
```

E um link na página inicial (`projetos/templates/projetos/index.html`):

```html
<body class="p-4">
    <a href="{% url 'dashboard' %}" class="btn btn-info mb-3 ms-2">
      Ver Dashboard
    </a>
    
    <ul class="list-group">
```

-----

## Encerrando o tutorial

Neste módulo, você aprendeu a expandir um sistema Django de forma profissional:

  * Criou páginas com parâmetros dinâmicos;
  * Implementou login e logout com segurança;
  * Melhorou formulários com o `crispy-forms`;
  * Configurou um banco PostgreSQL/MySQL;
  * E construiu um dashboard interativo com Plotly.

Esses recursos formam a base de qualquer sistema web moderno — e agora você domina todos eles.