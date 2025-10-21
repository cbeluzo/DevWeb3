# 🧭 Tutorial 1 — Desenvolvimento Web Estruturado com Django

**Curso:** Sistemas Web em Python
**Duração sugerida:** 1 a 2 encontros (4 – 6 horas)
**Objetivo geral:** desenvolver um sistema web completo com o framework Django, aplicando princípios de arquitetura MVT, persistência de dados e controle de rotas.

-----

## 1\. Introdução ao Django

Neste primeiro encontro, o meu objetivo é conduzi-lo à construção de um sistema web real utilizando o **Django**, um dos frameworks Python mais maduros e robustos da atualidade.

Quando começamos a trabalhar com desenvolvimento web, é comum lidarmos com muitas camadas diferentes — servidor, rotas, banco de dados, autenticação, interface, entre outras. O Django foi concebido exatamente para integrar todos esses elementos de forma coesa, dentro de um mesmo ecossistema.

O Django segue o padrão **Model-View-Template (MVT)**, que é uma adaptação do modelo **MVC (Model-View-Controller)**.
No Django, o fluxo de execução é organizado assim:

  * **Model:** representa as estruturas de dados e contém a lógica de acesso ao banco;
  * **View:** processa as requisições HTTP e prepara os dados para apresentação;
  * **Template:** define a camada de visualização HTML.

Além disso, o Django inclui um servidor interno para testes, um sistema de autenticação, um painel administrativo, proteção contra vulnerabilidades comuns e um ORM (Object Relational Mapping) para manipular dados sem escrever SQL diretamente.

Ao longo deste tutorial, vou guiá-lo passo a passo na construção de um pequeno **sistema de gestão de projetos**, explorando a estrutura do framework e as boas práticas de engenharia web.

-----

## 2\. Preparação do Ambiente no Ubuntu

Antes de programar, gosto de garantir que todos os alunos tenham o mesmo ambiente configurado. Assim, evitamos erros de versão e compreendemos como cada dependência se encaixa.

### 2.1. Atualizando o sistema

No Ubuntu, começo sempre atualizando os pacotes existentes:

```bash
sudo apt update && sudo apt upgrade -y
```

Esse comando sincroniza os repositórios e instala as versões mais recentes. Essa prática é essencial para reduzir conflitos e manter o sistema seguro.

-----

### 2.2. Verificando a versão do Python

Em seguida, verifico se o Python já está instalado e qual versão está ativa:

```bash
python3 --version
```

O Django exige **Python 3.8 ou superior**. Eu recomendo **Python 3.11**, que traz melhor desempenho e compatibilidade com bibliotecas modernas.

-----

### 2.3. Instalando dependências básicas

Agora instalo as ferramentas necessárias:

```bash
sudo apt install python3-pip python3-venv python3-dev build-essential libpq-dev -y
```

Cada item tem uma função específica:

  * `pip` é o gerenciador de pacotes do Python;
  * `venv` cria ambientes virtuais isolados;
  * `python3-dev` e `build-essential` são necessários para compilar extensões;
  * `libpq-dev` é uma dependência do PostgreSQL (que usaremos mais adiante).

-----

## 3\. Criação do Projeto e do Ambiente Virtual

Quando inicio um projeto Python, sempre crio um **ambiente virtual**. Essa prática evita que versões diferentes de bibliotecas entrem em conflito.

### 3.1. Criando o diretório do projeto

```bash
mkdir ~/django_project
cd ~/django_project
```

Aqui estou criando uma pasta específica para o projeto dentro do diretório pessoal.

-----

### 3.2. Criando o ambiente virtual

```bash
python3 -m venv venv
```

Esse comando cria uma cópia isolada do Python e do `pip`. Dentro dela instalaremos todas as dependências deste projeto, sem interferir em outros.

-----

### 3.3. Ativando o ambiente

```bash
source venv/bin/activate
```

Quando o ambiente virtual é ativado, o terminal passa a exibir o prefixo `(venv)`. Isso significa que, a partir desse ponto, todos os comandos Python e pip afetarão apenas este projeto.

-----

### 3.4. Atualizando o pip

```bash
pip install --upgrade pip
```

É importante manter o pip atualizado para evitar incompatibilidades com versões recentes de pacotes.

-----

## 4\. Instalação do Django e Bibliotecas Complementares

Com o ambiente ativo, instalo o Django e alguns pacotes que facilitam o desenvolvimento:

```bash
pip install django==5.1 psycopg2-binary django-crispy-forms
```

Explico brevemente o papel de cada biblioteca:

  * **Django** é o núcleo do nosso framework;
  * **psycopg2-binary** é o driver de conexão com bancos PostgreSQL;
  * **django-crispy-forms** permite integrar Bootstrap e melhorar a aparência de formulários.

Depois registro as dependências para replicar o ambiente facilmente:

```bash
pip freeze > requirements.txt
```

O arquivo `requirements.txt` é um registro exato das versões instaladas e será essencial para reproduzir o projeto em outro computador.

-----

## 5\. Estrutura Inicial do Projeto Django

### 5.1. Criando o projeto

```bash
django-admin startproject gestao_projetos .
```

O ponto final (`.`) indica que o projeto será criado no diretório atual.
A estrutura resultante é:

```
django_project/
 ├── manage.py
 ├── gestao_projetos/
 │    ├── __init__.py
 │    ├── settings.py
 │    ├── urls.py
 │    ├── wsgi.py
 │    └── asgi.py
```

Cada arquivo tem uma função clara:

  * `manage.py` é o utilitário de comando do Django;
  * `settings.py` centraliza as configurações da aplicação;
  * `urls.py` define as rotas;
  * `wsgi.py` e `asgi.py` permitem a integração com servidores web.

-----

### 5.2. Testando o servidor interno

```bash
python manage.py runserver
```

Ao executar esse comando, o Django inicia um pequeno servidor de desenvolvimento.
Acesso no navegador o endereço [http://127.0.0.1:8000](http://127.0.0.1:8000).

Se tudo estiver correto, vejo a mensagem “The install worked successfully”. Nesse momento o ambiente está funcionando e posso prosseguir.

-----

## 6\. Criando o Aplicativo Principal

O Django organiza um projeto em **aplicativos** (apps). Cada app representa uma parte funcional da aplicação.

### 6.1. Criando o app “projetos”

```bash
python manage.py startapp projetos
```

Esse comando cria uma nova pasta `projetos/`, onde implementarei os modelos, views e templates.

-----

### 6.2. Registrando o aplicativo

Para que o Django reconheça o novo app, edito o arquivo `gestao_projetos/settings.py` e adiciono `projetos` e `crispy_forms` à lista `INSTALLED_APPS`:

```python
# gestao_projetos/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Meus aplicativos
    "projetos",
    # Aplicativos de terceiros
    "crispy_forms",
]
```

Como também instalamos o `crispy_forms`, aproveito para configurá-lo. Ao final do arquivo `settings.py`, adiciono:

```python
# gestao_projetos/settings.py (ao final do arquivo)

# Configuração para o django-crispy-forms (usará Bootstrap 5)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

-----

## 7\. Modelagem de Dados (Camada Model)

Agora começo a definir as entidades principais do sistema. No nosso caso, trabalharemos com **Projetos** e **Tarefas**.

Edito `projetos/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User

class Projeto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Tarefa(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
```

Aqui, o modelo `Projeto` representa um projeto cadastrado, enquanto `Tarefa` representa atividades vinculadas.
As chaves estrangeiras (`ForeignKey`) garantem a relação um-para-muitos entre projetos e tarefas.

-----

## 8\. Criação do Banco e Migrações

No Django, não criamos tabelas manualmente: usamos **migrações**.

```bash
python manage.py makemigrations
python manage.py migrate
```

  * `makemigrations` gera scripts de alteração conforme os modelos;
  * `migrate` executa esses scripts no banco de dados (SQLite por padrão).

Essa automação é um dos pontos fortes do Django, pois mantém o esquema de dados versionado e reproduzível.

-----

## 9\. Criando um Usuário Administrador

Para acessar o painel administrativo, crio um **superusuário**:

```bash
python manage.py createsuperuser
```

O terminal solicitará nome de usuário, e-mail e senha.
Esse login permitirá gerenciar projetos e tarefas diretamente pela interface gráfica.

-----

## 10\. Registro dos Modelos no Painel Administrativo

Edito `projetos/admin.py` para tornar os modelos visíveis no admin:

```python
from django.contrib import admin
from .models import Projeto, Tarefa

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ("nome", "responsavel", "data_inicio", "data_fim")
    search_fields = ("nome", "responsavel__username")

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "projeto", "concluida")
    list_filter = ("concluida",)
```

Essa configuração permite pesquisar e filtrar registros de forma amigável.

-----

## 11\. Criação das Rotas (Camada View/Controller)

Agora, defino as rotas de acesso. A boa prática no Django é encapsular as rotas de um aplicativo dentro dele mesmo, usando `include()`.

### 11.1. Rotas do Projeto Principal

Primeiro, edito o arquivo `gestao_projetos/urls.py` para que ele "inclua" as rotas do nosso aplicativo `projetos`:

```python
# gestao_projetos/urls.py

from django.contrib import admin
from django.urls import path, include  # Importo o 'include'

urlpatterns = [
    path("admin/", admin.site.urls),
    # Delega todas as rotas da raiz "" para o app 'projetos'
    path("", include("projetos.urls")), 
]
```

Isso torna o arquivo de rotas principal limpo e organizado.

### 11.2. Rotas do Aplicativo

Agora, crio o arquivo `projetos/urls.py` (que não existe por padrão) para gerenciar as rotas específicas deste app:

```python
# projetos/urls.py (CRIAR ESTE ARQUIVO)

from django.urls import path
from . import views  # Importa as views do app atual

urlpatterns = [
    path("", views.index, name="index"),
]
```

A rota raiz (`""`) agora chama a função `index()` definida no módulo `views` do app `projetos`.

-----

## 12\. Implementação da View e do Template

### 12.1. View

Em `projetos/views.py`, defino a lógica da nossa página inicial:

```python
# projetos/views.py

from django.shortcuts import render
from .models import Projeto

def index(request):
    projetos = Projeto.objects.all()
    # Usamos 'projetos/index.html' (com namespace)
    return render(request, "projetos/index.html", {"projetos": projetos})
```

Recupero todos os projetos do banco e os passo para o template. Note que usamos `projetos/index.html` na chamada do `render`. Esta é a boa prática de *namespacing* de templates, que veremos a seguir.

-----

### 12.2. Template

Para evitar conflitos (onde dois apps podem ter um `index.html`), criamos um subdiretório dentro de `templates/` com o nome do nosso app.

1.  Crio a pasta `templates` dentro de `projetos/`.
2.  **Importante:** Dentro de `templates/`, crio *outra* pasta chamada `projetos/`.
3.  Crio o arquivo `index.html` dentro dessa subpasta.

A estrutura final deve ser: `projetos/templates/projetos/index.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gestão de Projetos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
    <h1 class="mb-4">Projetos Cadastrados</h1>
    <ul class="list-group">
        {% for projeto in projetos %}
            <li class="list-group-item">
                <strong>{{ projeto.nome }}</strong> — {{ projeto.responsavel.username }}
            </li>
        {% empty %}
            <li class="list-group-item text-muted">Nenhum projeto cadastrado.</li>
        {% endfor %}
    </ul>
</body>
</html>
```

O sistema de templates do Django usa tags `{% ... %}` para controle de fluxo e expressões `{{ ... }}` para inserir dados no HTML.

-----

## 13\. Execução e Teste

Executo novamente o servidor:

```bash
python manage.py runserver
```

Agora tenho duas interfaces disponíveis:

  * **Painel administrativo:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
  * **Página principal:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

Ao cadastrar alguns projetos no admin (usando o superusuário criado na Seção 9), eles devem aparecer automaticamente na página inicial.

-----

## 14\. Extensões Sugeridas

Para consolidar o aprendizado, costumo propor extensões práticas:

1.  Criar uma página de detalhe de projeto (`/projeto/<id>/`);
2.  Implementar autenticação de usuários (login/logout);
3.  Integrar `django-crispy-forms` aos formulários HTML (já está configurado\!);
4.  Configurar um banco PostgreSQL;
5.  Explorar visualizações gráficas com Plotly (Tutorial 3).

Essas atividades aprofundam o domínio do framework e estimulam o raciocínio de engenharia.

-----

## 15\. Conclusão Didática

Com este primeiro tutorial, concluímos a **primeira iteração completa de um sistema web em Django**.
Conseguimos compreender, de forma estruturada:

  * o funcionamento do padrão **MVT**;
  * a configuração do ambiente de desenvolvimento;
  * a criação de aplicativos e modelos de dados;
  * a integração entre views e templates (seguindo boas práticas);
  * e o uso do painel administrativo para gerenciamento rápido.

Mais importante que o código em si é perceber **a metodologia de construção** — do ambiente virtual ao deploy local, passando por cada decisão arquitetural explicada passo a passo.

A partir daqui, nos próximos tutoriais, expandiremos esse projeto com camadas de autenticação, banco de dados relacional PostgreSQL e visualizações interativas.