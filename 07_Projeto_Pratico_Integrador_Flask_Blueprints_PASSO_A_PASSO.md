
# Projeto Prático Integrador com Flask (Passo a Passo)  

> Projeto: https://gamma.app/docs/Projeto-Pratico-Integrador-com-Flask-od3eh9fy8960yko

> Revisão Flask: https://gamma.app/docs/Bibliotecas-e-Recursos-do-Flask-hk99o6milzts49l

> Revisão WFT: https://gamma.app/docs/Flask-WTF-Recursos-e-Conceitos-Fundamentais-fl1mx3w4awcamyn

> Revisão CSRF • Autenticação (Flask-Login) • API RESTful: https://gamma.app/docs/CSRF-Autenticacao-com-Flask-Login-API-RESTful-69pg2ylq6uc0ra0

## Flask-WTF • CSRF • Autenticação (Flask-Login) • API RESTful • Blueprints • MySQL/PostgreSQL

Este roteiro reescreve o projeto integrador em **passos sequenciais**, com explicações de motivação técnica e trechos de código prontos para copiar e colar. A parte de **formulários, validação e CSRF** está alinhada ao tutorial de Flask‑WTF já fornecido (vide referência ao final).

---

## 0) Objetivo e visão geral

O objetivo é construir uma aplicação Flask **modular e segura** que ofereça: interface HTML com formulários, autenticação de usuários, proteção CSRF, CRUD completo para uma entidade de negócio e uma **API RESTful paralela** que exponha os mesmos dados em JSON. A organização em **Blueprints** separa o módulo **web** (páginas HTML) do módulo **api** (endpoints), facilitando manutenção e testes.

---

## 1) Preparar o ambiente e dependências

Crie e ative um ambiente virtual, depois instale as bibliotecas. Em Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install Flask Flask-WTF WTForms email-validator Flask-Login Flask-SQLAlchemy PyMySQL psycopg2-binary
```

Em Linux/macOS (bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install Flask Flask-WTF WTForms email-validator Flask-Login Flask-SQLAlchemy PyMySQL psycopg2-binary
```

Crie um `requirements.txt` para reprodutibilidade:
```bash
pip freeze > requirements.txt
```

---

## 2) Estrutura de diretórios e arquivos

Crie a seguinte estrutura mínima:
```
/meu_projeto
|-- app.py
|-- config.py
|-- models.py
|-- extensions.py
|-- /blueprints
|   |-- __init__.py
|   |-- /web
|   |   |-- __init__.py
|   |   |-- routes.py
|   |   |-- forms.py
|   |-- /api
|       |-- __init__.py
|       |-- routes.py
|-- /templates
|   |-- layout.html
|   |-- login.html
|   |-- registro.html
|   |-- lista.html
|   |-- editar.html
|-- /static
|   |-- css/
|   |-- img/
|-- /uploads
|-- requirements.txt
```

A pasta `/uploads` será usada se a sua entidade tiver upload de arquivos (opcional).

---

## 3) Configurações da aplicação

No `config.py`, centralize chaves e a URL do banco. Use **variáveis de ambiente** em produção para ocultar segredos.

```python
# config.py
import os

# Classe de configuração centralizada para a aplicação Flask
# O uso de classes facilita trocar ambientes (ex.: Desenvolvimento, Teste, Produção)
class Config:
    # Chave secreta usada pelo Flask para:
    #   - Assinar cookies de sessão
    #   - Gerar e validar tokens CSRF (usados em formulários Flask-WTF)
    # Em produção, o valor deve vir de uma variável de ambiente (SECRET_KEY).
    # Se não houver, usa um valor padrão inseguro (apenas para desenvolvimento).
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

    # URL de conexão com o banco de dados
    # É buscada da variável de ambiente DATABASE_URL.
    # Se não estiver definida, usa um valor padrão para MySQL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        # Padrão para MySQL usando o driver PyMySQL
        "mysql+pymysql://usuario:senha@localhost/meuprojeto"
        # Alternativa para PostgreSQL com psycopg2 (descomentar para usar):
        # "postgresql+psycopg2://usuario:senha@localhost/meuprojeto"
    )

    # Evita que o SQLAlchemy monitore modificações de objetos em memória.
    # Isso reduz overhead e evita warnings desnecessários.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Caminho absoluto para a pasta de uploads, baseado no diretório deste arquivo.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

    # Define o tamanho máximo aceito para uploads de arquivos (em bytes).
    # Neste caso: 16 MB (16 * 1024 * 1024).
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
```

Em Windows (PowerShell) para testes locais:
```powershell
$env:SECRET_KEY="uma-chave-forte"
$env:DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost/meuprojeto"
```

---

## 4) Extensões: banco e login

```python
# extensions.py
# Importa a extensão SQLAlchemy para integração do Flask com bancos de dados relacionais.
# O SQLAlchemy fornece um ORM (Object Relational Mapper), permitindo trabalhar com tabelas
# e consultas usando classes e objetos Python, ao invés de SQL puro.
from flask_sqlalchemy import SQLAlchemy

# Importa o gerenciador de login do Flask-Login.
# Essa extensão facilita autenticação e gerenciamento de sessões de usuários.
from flask_login import LoginManager


# Cria a instância do banco de dados.
# Ela será inicializada posteriormente dentro da aplicação (app) com db.init_app(app).
db = SQLAlchemy()

# Cria a instância do gerenciador de login.
# Ele vai cuidar de login, logout, lembrar sessão do usuário e rotas protegidas.
login_manager = LoginManager()

# Define para onde o usuário será redirecionado caso tente acessar uma rota protegida
# sem estar autenticado. Neste caso, envia para a rota 'login' do blueprint 'web'.
login_manager.login_view = "web.login"

```

---

## 5) Modelos e hashing de senha

```python
# models.py
# Importa a classe UserMixin do Flask-Login.
# Ela adiciona automaticamente atributos e métodos úteis para autenticação,
# como is_authenticated, is_active e get_id().
from flask_login import UserMixin

# Importa funções para gerar e verificar hashes de senha.
# Nunca devemos armazenar senhas em texto puro, e sim o hash seguro.
from werkzeug.security import generate_password_hash, check_password_hash

# Importa a instância do SQLAlchemy criada em extensions.py
from extensions import db


# ---------------------------
# Modelo de Usuário
# ---------------------------
class Usuario(UserMixin, db.Model):
    # Identificador único (chave primária)
    id = db.Column(db.Integer, primary_key=True)

    # Nome do usuário (não pode ser nulo)
    nome = db.Column(db.String(50), nullable=False)

    # Email do usuário, obrigatório e único no banco
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Hash da senha, nunca armazenamos a senha em texto puro
    senha_hash = db.Column(db.String(128), nullable=False)

    # Método para definir a senha do usuário
    # Recebe a senha em texto, gera o hash e armazena em senha_hash
    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    # Método para verificar se a senha fornecida bate com o hash armazenado
    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)


# ---------------------------
# Modelo de Entidade de negócio (CRUD genérico)
# ---------------------------
class Entidade(db.Model):
    # Identificador único (chave primária)
    id = db.Column(db.Integer, primary_key=True)

    # Campo obrigatório (ex.: título)
    campo1 = db.Column(db.String(150), nullable=False)

    # Campo obrigatório (ex.: autor)
    campo2 = db.Column(db.String(100), nullable=False)

    # Campo opcional (ex.: ISBN)
    campo3 = db.Column(db.String(50))

```

---

## 6) Fábrica da aplicação e registro de blueprints

```python
# app.py
# Importa a classe principal do Flask
from flask import Flask

# Importa a classe de configuração centralizada (SECRET_KEY, banco etc.)
from config import Config

# Importa extensões inicializadas em extensions.py
from extensions import db, login_manager

# Importa o modelo de usuário (necessário para autenticação com Flask-Login)
from models import Usuario

# Importa os blueprints para separar rotas web (HTML) e API (JSON)
from blueprints.web import web_bp
from blueprints.api import api_bp


# ---------------------------
# Fábrica da aplicação Flask
# ---------------------------
def create_app():
    # Cria a instância principal do Flask
    app = Flask(__name__)

    # Carrega as configurações da classe Config
    app.config.from_object(Config)

    # Inicializa as extensões com o app
    db.init_app(app)
    login_manager.init_app(app)

    # Callback usado pelo Flask-Login para carregar usuário logado
    @login_manager.user_loader
    def load_user(user_id):
        # Recupera usuário pelo ID (conversão para int é necessária)
        return Usuario.query.get(int(user_id))

    # Registra o blueprint responsável pelas páginas web (HTML)
    app.register_blueprint(web_bp)

    # Registra o blueprint responsável pela API RESTful
    # O prefixo /api é adicionado automaticamente às rotas desse módulo
    app.register_blueprint(api_bp, url_prefix="/api")

    # Cria as tabelas no banco (somente para início rápido)
    # Em produção, use migrações (Alembic/Flask-Migrate)
    with app.app_context():
        db.create_all()

    return app


# ---------------------------
# Ponto de entrada da aplicação
# ---------------------------
if __name__ == "__main__":
    # Cria a aplicação Flask usando a fábrica
    app = create_app()

    # Executa o servidor em modo debug (útil para desenvolvimento)
    app.run(debug=True)
```

A função `create_app` segue o padrão **application factory**; isso facilita testes e deploy.

---

## 7) Blueprint WEB: formulários e rotas HTML

### 7.1 Inicialização do blueprint e formulários

```python
# blueprints/web/__init__.py
from flask import Blueprint

# Cria o blueprint "web", que agrupa as rotas e lógica da interface HTML
# Parâmetros:
#   - "web": nome interno do blueprint
#   - __name__: módulo atual
#   - template_folder="../templates": indica onde estão os arquivos HTML (Jinja2)
web_bp = Blueprint("web", __name__, template_folder="../templates")

# Importa as rotas associadas a esse blueprint
# O comentário "# noqa" serve para ferramentas de lint não acusarem import não usado
from . import routes  # noqa

```

```python
# blueprints/web/forms.py
# blueprints/web/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# ---------------------------
# Formulário de Registro
# ---------------------------
class RegistroForm(FlaskForm):
    # Campo de nome do usuário
    # Validações:
    #   - DataRequired: não pode ser vazio
    #   - Length: mínimo de 3 e máximo de 50 caracteres
    nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])

    # Campo de email do usuário
    # Validações:
    #   - DataRequired: obrigatório
    #   - Email: deve ter formato válido de email
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Campo de senha
    # Validações:
    #   - DataRequired: obrigatório
    #   - Length: pelo menos 6 caracteres
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])

    # Campo de confirmação de senha
    # Validação:
    #   - EqualTo("senha"): deve ser igual ao campo senha
    confirmar = PasswordField("Confirmar Senha", validators=[EqualTo("senha")])

    # Botão de envio do formulário
    submit = SubmitField("Registrar")


# ---------------------------
# Formulário de Login
# ---------------------------
class LoginForm(FlaskForm):
    # Campo de email do usuário
    # Validações:
    #   - DataRequired: obrigatório
    #   - Email: exige formato válido de email
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Campo de senha
    # Validação:
    #   - DataRequired: obrigatório
    senha = PasswordField("Senha", validators=[DataRequired()])

    # Botão de envio
    submit = SubmitField("Entrar")
```

### 7.2 Rotas HTML (login/registro/CRUD básico)

```python
# blueprints/web/routes.py
# Importa funções utilitárias do Flask
from flask import render_template, redirect, url_for, flash, request

# Importa funções do Flask-Login para autenticação e controle de acesso
from flask_login import login_user, logout_user, login_required, current_user

# Importa o blueprint definido em __init__.py
from . import web_bp

# Importa os formulários usados nesta camada
from .forms import LoginForm, RegistroForm

# Importa extensões (banco de dados)
from extensions import db

# Importa os modelos do sistema
from models import Usuario, Entidade


# ---------------------------
# Rota inicial (home)
# ---------------------------
@web_bp.route("/")
def index():
    # Apenas renderiza o layout base
    return render_template("layout.html")


# ---------------------------
# Registro de novo usuário
# ---------------------------
@web_bp.route("/registro", methods=["GET", "POST"])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        # Verifica se já existe usuário com o mesmo email
        if Usuario.query.filter_by(email=form.email.data).first():
            flash("E-mail já cadastrado.", "warning")
            return redirect(url_for("web.registro"))
        
        # Cria novo usuário com hash da senha
        u = Usuario(nome=form.nome.data, email=form.email.data)
        u.set_senha(form.senha.data)
        
        # Salva no banco
        db.session.add(u)
        db.session.commit()
        
        flash("Conta criada. Faça login.", "success")
        return redirect(url_for("web.login"))
    
    # Exibe formulário (GET ou se houver erro)
    return render_template("registro.html", form=form)


# ---------------------------
# Login de usuário
# ---------------------------
@web_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Procura usuário pelo email
        u = Usuario.query.filter_by(email=form.email.data).first()
        
        # Confere se usuário existe e se a senha está correta
        if u and u.check_senha(form.senha.data):
            login_user(u)  # Inicia a sessão do usuário
            return redirect(url_for("web.lista"))
        
        # Se falhar, mostra mensagem de erro
        flash("Credenciais inválidas.", "danger")
    
    # Renderiza formulário de login
    return render_template("login.html", form=form)


# ---------------------------
# Logout de usuário
# ---------------------------
@web_bp.route("/logout")
@login_required
def logout():
    logout_user()  # Encerra a sessão
    return redirect(url_for("web.login"))


# ---------------------------
# Lista de entidades (CRUD - Read)
# ---------------------------
@web_bp.route("/entidades")
@login_required
def lista():
    # Captura parâmetro de busca da URL (?q=...)
    q = request.args.get("q", "").strip()
    query = Entidade.query

    if q:
        # Busca simples em dois campos usando LIKE
        query = query.filter(
            (Entidade.campo1.ilike(f"%{q}%")) | (Entidade.campo2.ilike(f"%{q}%"))
        )
    
    # Ordena por ID decrescente
    itens = query.order_by(Entidade.id.desc()).all()
    
    return render_template("lista.html", itens=itens, busca=q)


# ---------------------------
# Criação de nova entidade (CRUD - Create)
# ---------------------------
@web_bp.route("/entidades/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        # Cria objeto Entidade com dados do formulário
        e = Entidade(
            campo1=request.form.get("campo1"),
            campo2=request.form.get("campo2"),
            campo3=request.form.get("campo3"),
        )
        db.session.add(e)
        db.session.commit()
        flash("Registro criado.", "success")
        return redirect(url_for("web.lista"))
    
    # GET → exibe formulário vazio
    return render_template("editar.html", item=None)


# ---------------------------
# Edição de entidade (CRUD - Update)
# ---------------------------
@web_bp.route("/entidades/<int:pk>/editar", methods=["GET", "POST"])
@login_required
def editar(pk):
    # Busca entidade pelo ID ou retorna 404
    e = Entidade.query.get_or_404(pk)

    if request.method == "POST":
        # Atualiza campos
        e.campo1 = request.form.get("campo1")
        e.campo2 = request.form.get("campo2")
        e.campo3 = request.form.get("campo3")
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("web.lista"))
    
    # GET → exibe formulário preenchido
    return render_template("editar.html", item=e)


# ---------------------------
# Exclusão de entidade (CRUD - Delete)
# ---------------------------
@web_bp.route("/entidades/<int:pk>/excluir", methods=["POST"])
@login_required
def excluir(pk):
    # Busca entidade ou retorna 404
    e = Entidade.query.get_or_404(pk)
    db.session.delete(e)
    db.session.commit()
    flash("Registro excluído.", "info")
    return redirect(url_for("web.lista"))
```

As rotas HTML usam **CSRF automaticamente** via Flask‑WTF nos formulários. Para entender o porquê e as regras de validação, consulte o material de Flask‑WTF indicado na referência ao final.

---

## 8) Blueprint API: endpoints RESTful

```python
# blueprints/api/__init__.py
# Importa a classe Blueprint do Flask.
# O Blueprint é usado para modularizar a aplicação,
# permitindo separar rotas da API das rotas da interface web.
from flask import Blueprint

# Cria o blueprint chamado "api".
# Parâmetros:
#   - "api": nome interno do blueprint (usado no url_for, por exemplo).
#   - __name__: referência ao módulo atual, necessária para o Flask localizar recursos.
api_bp = Blueprint("api", __name__)

# Importa o módulo de rotas que será registrado neste blueprint.
# O comentário "# noqa" indica para ferramentas de lint que este import
# não deve ser marcado como "não usado", pois é necessário para carregar as rotas.
from . import routes  # noqa

```

```python
# blueprints/api/routes.py
# Importa utilitários do Flask
from flask import jsonify, request, abort

# Importa extensões globais (banco de dados)
from extensions import db

# Importa o modelo de negócio
from models import Entidade

# Importa o blueprint "api" definido em __init__.py
from . import api_bp


# ---------------------------
# Função auxiliar para serializar objeto Entidade em dicionário
# ---------------------------
def to_dict(e: Entidade):
    return {
        "id": e.id,
        "campo1": e.campo1,
        "campo2": e.campo2,
        "campo3": e.campo3
    }


# ---------------------------
# GET /api/entidades
# Lista todas as entidades em ordem decrescente de ID
# ---------------------------
@api_bp.route("/entidades", methods=["GET"])
def api_listar():
    itens = Entidade.query.order_by(Entidade.id.desc()).all()
    return jsonify([to_dict(e) for e in itens]), 200


# ---------------------------
# GET /api/entidades/<id>
# Obtém uma entidade específica pelo ID
# ---------------------------
@api_bp.route("/entidades/<int:pk>", methods=["GET"])
def api_obter(pk):
    e = Entidade.query.get_or_404(pk)  # retorna 404 se não existir
    return jsonify(to_dict(e)), 200


# ---------------------------
# POST /api/entidades
# Cria uma nova entidade a partir de dados JSON
# ---------------------------
@api_bp.route("/entidades", methods=["POST"])
def api_criar():
    dados = request.get_json(silent=True) or {}

    # Valida campos obrigatórios
    if not all(k in dados for k in ("campo1", "campo2")):
        abort(400, description="Campos obrigatórios: campo1, campo2")

    # Cria nova instância
    e = Entidade(
        campo1=dados["campo1"],
        campo2=dados["campo2"],
        campo3=dados.get("campo3")
    )

    db.session.add(e)
    db.session.commit()

    return jsonify(to_dict(e)), 201  # 201 = Created


# ---------------------------
# PUT/PATCH /api/entidades/<id>
# Atualiza uma entidade existente
# ---------------------------
@api_bp.route("/entidades/<int:pk>", methods=["PUT", "PATCH"])
def api_atualizar(pk):
    e = Entidade.query.get_or_404(pk)
    dados = request.get_json(silent=True) or {}

    # Atualiza apenas os campos presentes no JSON
    e.campo1 = dados.get("campo1", e.campo1)
    e.campo2 = dados.get("campo2", e.campo2)
    e.campo3 = dados.get("campo3", e.campo3)

    db.session.commit()
    return jsonify(to_dict(e)), 200


# ---------------------------
# DELETE /api/entidades/<id>
# Exclui uma entidade existente
# ---------------------------
@api_bp.route("/entidades/<int:pk>", methods=["DELETE"])
def api_excluir(pk):
    e = Entidade.query.get_or_404(pk)
    db.session.delete(e)
    db.session.commit()
    return jsonify({"mensagem": "Excluído"}), 200
```

A API retorna **JSON** e usa **códigos HTTP adequados** (`200/201/400/404`). Em cenários avançados, adicione autenticação por **token/JWT** para proteger endpoints.

---

## 9) Templates mínimos

`templates/layout.html` (layout base com flash messages):
```html
<!doctype html>
<html lang="pt-br">
  <head>
    <!-- Define o tipo de documento HTML5 -->
    <meta charset="utf-8" />

    <!-- Configuração para responsividade em dispositivos móveis -->
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <!-- Título da aplicação (aparece na aba do navegador) -->
    <title>Projeto Flask</title>
  </head>
  <body>

    <!-- Bloco para exibir mensagens flash enviadas pelo backend -->
    {% with mensagens = get_flashed_messages(with_categories=true) %}
      {% if mensagens %}
        <ul>
          {% for cat, msg in mensagens %}
            <!-- Cada mensagem recebe uma classe CSS com a categoria (ex.: success, danger, info),
                 que pode ser usada para estilizar cores e ícones -->
            <li class="{{ cat }}">{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <!-- Área principal da página.
         O conteúdo específico de cada template será inserido aqui
         através do mecanismo de herança de templates Jinja2 -->
    <main>
      {% block content %}{% endblock %}
    </main>

  </body>
</html>

```

`templates/login.html`:
```html
{# Este template herda a estrutura base de layout.html #}
{% extends "layout.html" %}

{# Substitui o bloco "content" definido no layout.html #}
{% block content %}
  <h2>Login</h2>

  <!-- Formulário de login -->
  <form method="POST">
    {# Insere o token CSRF (Cross-Site Request Forgery) necessário para segurança #}
    {{ csrf_token() }}

    <!-- Campo de email -->
    <input name="email" type="email" placeholder="Email" required>

    <!-- Campo de senha -->
    <input name="senha" type="password" placeholder="Senha" required>

    <!-- Botão de envio -->
    <button type="submit">Entrar</button>
  </form>

  <!-- Link para a página de registro de novos usuários -->
  <p>
    Ainda não tem conta?
    <a href="{{ url_for('web.registro') }}">Registre-se</a>
  </p>
{% endblock %}

```

`templates/registro.html`:
```html
{# Este template herda o layout base (layout.html), que já contém a estrutura HTML principal e exibição de mensagens flash #}
{% extends "layout.html" %}

{# Substitui o bloco "content" definido no layout base #}
{% block content %}
  <h2>Registro</h2>

  <!-- Formulário de criação de conta -->
  <form method="POST">
    {# Token CSRF para proteger contra ataques de falsificação de requisições #}
    {{ csrf_token() }}

    <!-- Campo para o nome completo -->
    <input name="nome" placeholder="Nome" required>

    <!-- Campo de email (validação automática de formato pelo navegador) -->
    <input name="email" type="email" placeholder="Email" required>

    <!-- Campo de senha -->
    <input name="senha" type="password" placeholder="Senha" required>

    <!-- Campo de confirmação de senha (deve ser igual à senha) -->
    <input name="confirmar" type="password" placeholder="Confirmar senha" required>

    <!-- Botão para enviar os dados -->
    <button type="submit">Criar conta</button>
  </form>
{% endblock %}

```

`templates/lista.html` e `templates/editar.html` podem seguir o padrão básico de formulários HTML exibidos pelas rotas do blueprint **web**.

> Para **formularização com Flask‑WTF e mensagens de erro mais ricas**, utilize classes `FlaskForm` no módulo `forms.py` e os padrões demonstrados no tutorial específico de Flask‑WTF (campos, validadores e CSRF).

---
Boa! Sua parte de inicialização e execução já está clara, mas podemos deixá-la **mais didática e passo a passo**, para que até quem nunca rodou Flask com banco consiga entender. Veja uma versão revisada:

---

## 10) Inicializar o banco e executar o projeto

Antes de rodar a aplicação, verifique:

1. O servidor de banco de dados (MySQL ou PostgreSQL) está ativo?
2. O usuário e o banco definidos no `config.py` existem?
3. Você está dentro da pasta do projeto no terminal?

Se tudo estiver ok, siga as instruções abaixo para iniciar o servidor Flask em modo de desenvolvimento.

### Windows (PowerShell)

```powershell
# Defina o módulo principal da aplicação (app:create_app → função de fábrica)
$env:FLASK_APP="app:create_app"

# Ative o modo de desenvolvimento (debug ativado, reload automático)
$env:FLASK_ENV="development"

# Rode o servidor Flask
flask run
```

### Linux/macOS (bash)

```bash
# Defina o módulo principal da aplicação
export FLASK_APP="app:create_app"

# Ative o modo de desenvolvimento
export FLASK_ENV="development"

# Rode o servidor Flask
flask run
```

### Testando no navegador

Abra no seu navegador:
👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Você deverá ver a página inicial definida no blueprint **web**.

### Testando a API com `curl`

Você também pode testar os endpoints da API RESTful diretamente pelo terminal (ou via Postman/Insomnia).

Listar entidades:

```bash
curl http://127.0.0.1:5000/api/entidades
```

Criar uma nova entidade:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"campo1":"Exemplo","campo2":"Autor","campo3":"Opcional"}' \
     http://127.0.0.1:5000/api/entidades
```

Se tudo funcionar, você verá a resposta em formato JSON confirmando a criação do registro.

---

## 11) Boas práticas e próximos passos

Agora que sua aplicação está funcionando em ambiente de desenvolvimento, pense em ajustes para produção:

* **Segurança**: use HTTPS e nunca exponha sua `SECRET_KEY` ou credenciais de banco no código. Armazene tudo em variáveis de ambiente.
* **Banco de dados**: em vez de `db.create_all()`, use migrações com **Alembic** ou **Flask-Migrate** para versionar o esquema.
* **API**: para proteger endpoints da API, considere usar autenticação baseada em tokens (JWT ou OAuth2).
* **Uploads**: sempre valide extensões e tamanho dos arquivos, salve com `secure_filename`, e prefira armazenar em serviços externos como **Amazon S3** ou **Google Cloud Storage**.

---

📌 **Referência didática (Flask-WTF, validação e CSRF)**
A modelagem de formulários, a proteção contra CSRF e as práticas de renderização em Jinja2 seguem o **tutorial dedicado de Flask-WTF** já fornecido ao curso. Revise esse material para aprofundar-se em formulários, validações personalizadas e boas práticas de segurança.

---

---

## 🔑 Configurando variáveis de ambiente

Na prática, nunca devemos deixar senhas e chaves secretas fixas no código (hardcoded). Em vez disso, usamos variáveis de ambiente, que ficam fora do repositório e podem ser diferentes em cada máquina/servidor.

### Windows (PowerShell)

```powershell
# Defina a chave secreta usada pelo Flask para sessão e CSRF
$env:SECRET_KEY="minha-chave-super-secreta"

# Defina a URL de conexão com o banco de dados PostgreSQL
$env:DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost/meuprojeto"

# Se usar MySQL (com PyMySQL):
$env:DATABASE_URL="mysql+pymysql://usuario:senha@localhost/meuprojeto"

# Agora rode o Flask apontando para a função create_app
$env:FLASK_APP="app:create_app"
$env:FLASK_ENV="development"
flask run
```

### Linux/macOS (bash)

```bash
# Defina a chave secreta
export SECRET_KEY="minha-chave-super-secreta"

# Defina a URL de conexão com o banco
export DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost/meuprojeto"

# Para MySQL (com PyMySQL):
export DATABASE_URL="mysql+pymysql://usuario:senha@localhost/meuprojeto"

# Agora rode o Flask
export FLASK_APP="app:create_app"
export FLASK_ENV="development"
flask run
```

---

📌 **Explicando cada variável**:

* `SECRET_KEY` → usada para assinar cookies de sessão e tokens CSRF.
* `DATABASE_URL` → string de conexão SQLAlchemy (PostgreSQL ou MySQL).
* `FLASK_APP` → indica o ponto de entrada da aplicação (`app:create_app`).
* `FLASK_ENV=development` → ativa debug e reload automático (não usar em produção).

---


## 🌐 Exemplos de `DATABASE_URL`

| Banco de Dados   | Driver SQLAlchemy     | Exemplo de `DATABASE_URL`                                       |
| ---------------- | --------------------- | --------------------------------------------------------------- |
| **PostgreSQL**   | `postgresql+psycopg2` | `postgresql+psycopg2://usuario:senha@localhost:5432/meuprojeto` |
| **MySQL**        | `mysql+pymysql`       | `mysql+pymysql://usuario:senha@localhost:3306/meuprojeto`       |
| **SQLite**       | `sqlite`              | `sqlite:///meuprojeto.db` (arquivo local na raiz do projeto)    |
| **SQLite (abs)** | `sqlite`              | `sqlite:////caminho/absoluto/meuprojeto.db`                     |

---

## 🔑 Exemplos de configuração no terminal

### Windows (PowerShell)

```powershell
# PostgreSQL
$env:DATABASE_URL="postgresql+psycopg2://meuusuario:minhasenha@localhost:5432/meuprojeto"

# MySQL
$env:DATABASE_URL="mysql+pymysql://meuusuario:minhasenha@localhost:3306/meuprojeto"

# SQLite (arquivo local)
$env:DATABASE_URL="sqlite:///meuprojeto.db"
```

### Linux/macOS (bash)

```bash
# PostgreSQL
export DATABASE_URL="postgresql+psycopg2://meuusuario:minhasenha@localhost:5432/meuprojeto"

# MySQL
export DATABASE_URL="mysql+pymysql://meuusuario:minhasenha@localhost:3306/meuprojeto"

# SQLite (arquivo local)
export DATABASE_URL="sqlite:///meuprojeto.db"
```

---

📌 **Notas didáticas para os alunos**:

* `usuario:senha` → devem ser substituídos pelas credenciais reais do banco.
* `localhost:5432` ou `localhost:3306` → podem ser substituídos pelo IP/porta do servidor de banco.
* `sqlite:///` → usa **três barras** para caminho relativo e **quatro barras** (`////`) para caminho absoluto.
* Para testes rápidos, o SQLite é o mais simples, pois não exige instalação de servidor.

---

Perfeito 👌 Aqui está um **guia rápido em Markdown** com os erros mais comuns que os alunos podem encontrar ao configurar o banco no Flask/SQLAlchemy, junto com explicações e soluções.

---

# 💡 Guia Rápido – Erros Comuns em Configuração de Banco com Flask/SQLAlchemy

## 1. Erro de autenticação (usuário/senha incorretos)

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  password authentication failed for user "usuario"
```

🔎 **Causa:**
O usuário ou senha fornecidos na `DATABASE_URL` estão incorretos, ou o banco não está aceitando autenticação local.

✅ **Solução:**

* Verifique usuário e senha no banco (`psql`, `mysql` ou interface gráfica).
* Ajuste a string de conexão, ex.:

  ```bash
  export DATABASE_URL="postgresql+psycopg2://meuusuario:minhasenha@localhost:5432/meuprojeto"
  ```

---

## 2. Driver não encontrado

```
ModuleNotFoundError: No module named 'psycopg2'
```

ou

```
ModuleNotFoundError: No module named 'pymysql'
```

🔎 **Causa:**
O driver do banco não está instalado no ambiente virtual.

✅ **Solução:**
Instale o pacote correspondente:

```bash
pip install psycopg2-binary   # PostgreSQL
pip install PyMySQL           # MySQL
```

---

## 3. Banco ou tabela não existe

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "usuario" does not exist
```

🔎 **Causa:**
Você conectou ao banco, mas não rodou `db.create_all()` ou migrações.

✅ **Solução:**

* Crie as tabelas ao iniciar a aplicação:

  ```python
  with app.app_context():
      db.create_all()
  ```
* Em produção, use **Alembic** ou **Flask-Migrate** para gerenciar versões de schema.

---

## 4. Porta incorreta

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost' (111)")
```

🔎 **Causa:**
O cliente está tentando conectar na porta errada.

✅ **Solução:**

* MySQL → porta padrão **3306**
* PostgreSQL → porta padrão **5432**
* Ajuste na URL, ex.:

  ```bash
  export DATABASE_URL="mysql+pymysql://usuario:senha@localhost:3306/meuprojeto"
  ```

---

## 5. Problemas com SQLite

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

🔎 **Causa:**
O caminho para o arquivo SQLite não existe ou não tem permissão de escrita.

✅ **Solução:**

* Use caminho relativo (na raiz do projeto):

  ```bash
  export DATABASE_URL="sqlite:///meuprojeto.db"
  ```
* Ou caminho absoluto com quatro barras:

  ```bash
  export DATABASE_URL="sqlite:////home/usuario/projetos/meuprojeto.db"
  ```

---

📌 **Resumo para os alunos**:

1. Sempre conferir se o banco está rodando.
2. Conferir usuário, senha e porta.
3. Instalar os drivers corretos (`psycopg2-binary` ou `PyMySQL`).
4. Para começar rápido → usar `SQLite`.
5. Em produção → usar migrações para versionar o banco.

---

Ótimo 👌 Aqui está um **checklist de inicialização** em formato de quadro, pensado para ser usado como guia prático em sala ou até como slide no tutorial:

---

# ✅ Checklist de Inicialização do Projeto Flask + Banco

Antes de rodar `flask run`, confirme cada item abaixo:

| Etapa                        | O que verificar                                                                                                        | Comando/Exemplo                                                                                                                                                                                                                                                                                 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Ambiente virtual**      | Está criado e ativado?                                                                                                 | `python -m venv .venv` <br> `source .venv/bin/activate` (Linux/macOS) <br> `.\.venv\Scripts\Activate.ps1` (Windows)                                                                                                                                                                             |
| **2. Dependências**          | Todos os pacotes instalados (`Flask`, `Flask-WTF`, `Flask-Login`, `Flask-SQLAlchemy`, `psycopg2-binary` ou `PyMySQL`)? | `pip install -r requirements.txt`                                                                                                                                                                                                                                                               |
| **3. Banco de dados**        | O servidor está rodando (PostgreSQL/MySQL)? O banco e o usuário existem?                                               | `psql -U usuario -d meuprojeto` <br> `mysql -u usuario -p meuprojeto`                                                                                                                                                                                                                           |
| **4. Variáveis de ambiente** | `SECRET_KEY` e `DATABASE_URL` estão configuradas?                                                                      | Windows (PowerShell): <br> `$env:SECRET_KEY="chave-secreta"` <br> `$env:DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost/meuprojeto"` <br><br> Linux/macOS: <br> `export SECRET_KEY="chave-secreta"` <br> `export DATABASE_URL="mysql+pymysql://usuario:senha@localhost/meuprojeto"` |
| **5. Estrutura do projeto**  | Pastas e arquivos estão no lugar certo (`app.py`, `blueprints/`, `templates/`, `models.py`)?                           | verifique no explorador ou `tree` no terminal                                                                                                                                                                                                                                                   |
| **6. Criação das tabelas**   | As tabelas já foram criadas no banco?                                                                                  | No `app.py`: <br> `python <br> with app.app_context(): db.create_all() <br> `                                                                                                                                                                                                                   |
| **7. Execução**              | O servidor roda sem erro?                                                                                              | `flask run`                                                                                                                                                                                                                                                                                     |
| **8. Testes iniciais**       | Acesse a aplicação web e a API.                                                                                        | Navegador: [http://127.0.0.1:5000/](http://127.0.0.1:5000/) <br> API: `curl http://127.0.0.1:5000/api/entidades`                                                                                                                                                                                |

---

📌 **Dicas extras para alunos**:

* Se der erro, leia a mensagem com atenção → quase sempre indica **senha incorreta**, **driver faltando** ou **porta errada**.
* Para começar rápido, use **SQLite**, que não precisa de servidor externo.
* Sempre mantenha as variáveis sensíveis fora do código-fonte.

---


# 📝 Guia Prático – Campos mais utilizados em Flask-WTF

Todos os formulários herdam de `FlaskForm` e cada campo tem um tipo específico importado de `wtforms`.
Exemplo base:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, SelectMultipleField, RadioField, IntegerField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange
```

---

## 1) Campos de texto

### StringField

Campo de texto simples.

```python
nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])
```

👉 Uso: nomes, títulos, textos curtos.

---

## 2) Campo de senha

### PasswordField

Oculta os caracteres digitados.

```python
senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
```

👉 Uso: login, autenticação.

---

## 3) Campo de e-mail

### EmailField

Valida formato de e-mail automaticamente.

```python
from wtforms import EmailField
email = EmailField("E-mail", validators=[DataRequired(), Email()])
```

👉 Uso: cadastro de usuários, contatos.

---

## 4) Números

### IntegerField

Aceita apenas inteiros.

```python
idade = IntegerField("Idade", validators=[DataRequired(), NumberRange(min=0, max=120)])
```

### DecimalField

Aceita decimais (float).

```python
preco = DecimalField("Preço", validators=[DataRequired(), NumberRange(min=0)])
```

👉 Uso: formulários de produtos, finanças.

---

## 5) Área de texto

### TextAreaField

Campo multilinha.

```python
mensagem = TextAreaField("Mensagem", validators=[DataRequired(), Length(min=10)])
```

👉 Uso: descrições, observações.

---

## 6) Checkbox

### BooleanField

Caixa de seleção (verdadeiro/falso).

```python
aceite = BooleanField("Aceito os termos de uso", validators=[DataRequired()])
```

👉 Uso: consentimento, ativação/desativação de opções.

---

## 7) Radio buttons

### RadioField

Escolha **uma opção** entre várias.

```python
genero = RadioField("Gênero", choices=[("M", "Masculino"), ("F", "Feminino"), ("O", "Outro")])
```

👉 Uso: múltipla escolha simples.

---

## 8) Dropdown (Select)

### SelectField

Menu suspenso de escolha única.

```python
curso = SelectField("Curso", choices=[
    ("ads", "Análise e Desenvolvimento de Sistemas"),
    ("si", "Sistemas de Informação"),
    ("cc", "Ciência da Computação")
])
```

👉 Uso: selecionar categoria, status.

---

## 9) Lista múltipla

### SelectMultipleField

Permite selecionar várias opções ao mesmo tempo (Ctrl/Command + clique).

```python
tecnologias = SelectMultipleField("Tecnologias", choices=[
    ("py", "Python"),
    ("js", "JavaScript"),
    ("java", "Java"),
    ("cpp", "C++")
])
```

👉 Uso: tags, preferências múltiplas.

---

## 10) Datas

### DateField

Campo de seleção de data.

```python
nascimento = DateField("Data de nascimento", format="%Y-%m-%d")
```

👉 Uso: cadastros, eventos, prazos.

---

## 11) Upload de arquivos

### FileField

Para anexos e uploads.

```python
from flask_wtf.file import FileField, FileAllowed, FileRequired
arquivo = FileField("Arquivo", validators=[
    FileRequired(),
    FileAllowed(["jpg", "png", "pdf"], "Apenas imagens ou PDF!")
])
```

👉 Uso: upload de documentos, imagens.

---

## 12) Botão de envio

### SubmitField

Botão de envio do formulário.

```python
submit = SubmitField("Enviar")
```

---

# 📋 Exemplo de Formulário Completo

```python
class CadastroForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    email = EmailField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    idade = IntegerField("Idade", validators=[NumberRange(min=0)])
    genero = RadioField("Gênero", choices=[("M", "Masculino"), ("F", "Feminino")])
    curso = SelectField("Curso", choices=[("ads", "ADS"), ("si", "SI"), ("cc", "CC")])
    tecnologias = SelectMultipleField("Tecnologias", choices=[("py","Python"),("js","JavaScript")])
    aceite = BooleanField("Aceito os termos", validators=[DataRequired()])
    nascimento = DateField("Nascimento", format="%Y-%m-%d")
    arquivo = FileField("Currículo", validators=[FileAllowed(["pdf"], "Apenas PDF!")])
    submit = SubmitField("Registrar")
```

---

📌 **Resumo para os alunos**:

* Cada campo de formulário tem uma **classe própria** no WTForms.
* Sempre combine com **validadores** (`DataRequired`, `Email`, `Length`, `NumberRange`, etc.).
* A renderização no HTML pode ser feita direto com `{{ form.campo() }}` ou via macros para padronizar layout.


---

# 📊 Guia Rápido – Campos mais utilizados em Flask-WTF (WTForms)

| Campo (HTML)          | Classe WTForms        | Exemplo de código                                                                   | Uso típico                     |
| --------------------- | --------------------- | ----------------------------------------------------------------------------------- | ------------------------------ |
| **Texto**             | `StringField`         | `nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])`    | Nome, título, dados curtos     |
| **Senha**             | `PasswordField`       | `senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])`        | Login, autenticação            |
| **E-mail**            | `EmailField`          | `email = EmailField("E-mail", validators=[DataRequired(), Email()])`                | Cadastro de usuário            |
| **Número inteiro**    | `IntegerField`        | `idade = IntegerField("Idade", validators=[NumberRange(min=0, max=120)])`           | Idade, quantidade              |
| **Número decimal**    | `DecimalField`        | `preco = DecimalField("Preço", validators=[NumberRange(min=0)])`                    | Valores monetários             |
| **Área de texto**     | `TextAreaField`       | `mensagem = TextAreaField("Mensagem", validators=[DataRequired(), Length(min=10)])` | Descrição, observações         |
| **Checkbox**          | `BooleanField`        | `aceite = BooleanField("Aceito os termos", validators=[DataRequired()])`            | Consentimento, opções binárias |
| **Radio buttons**     | `RadioField`          | `genero = RadioField("Gênero", choices=[("M","Masculino"),("F","Feminino")])`       | Escolha única (sexo, plano)    |
| **Dropdown (select)** | `SelectField`         | `curso = SelectField("Curso", choices=[("ads","ADS"),("si","SI")])`                 | Categoria, status              |
| **Lista múltipla**    | `SelectMultipleField` | `tecnologias = SelectMultipleField("Tech", choices=[("py","Python"),("js","JS")])`  | Seleção de várias opções       |
| **Data**              | `DateField`           | `nascimento = DateField("Nascimento", format="%Y-%m-%d")`                           | Datas de cadastro, eventos     |
| **Upload de arquivo** | `FileField`           | `arquivo = FileField("Arquivo", validators=[FileAllowed(["pdf"],"Apenas PDF!")])`   | Upload de documentos/imagens   |
| **Botão enviar**      | `SubmitField`         | `submit = SubmitField("Enviar")`                                                    | Enviar formulário              |

---

📌 **Notas didáticas**:

* Todos os campos herdam de `FlaskForm`.
* Sempre associe **validadores** (`DataRequired`, `Email`, `Length`, `NumberRange`, etc.).
* Para uploads, use **`FileRequired`** e **`FileAllowed`** para garantir segurança.
* Os campos podem ser renderizados no template com `{{ form.campo() }}` ou customizados com macros.

---


