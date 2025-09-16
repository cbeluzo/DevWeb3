# Projeto Prático Integrador com Flask (Passo a Passo)  
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

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    # Escolha UMA das URLs abaixo. Em produção, use a variável DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        # MySQL (com PyMySQL):
        "mysql+pymysql://usuario:senha@localhost/meuprojeto"
        # PostgreSQL (com psycopg2-binary):
        # "postgresql+psycopg2://usuario:senha@localhost/meuprojeto"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
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
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "web.login"  # rota de login do blueprint 'web'
```

---

## 5) Modelos e hashing de senha

```python
# models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

# Entidade de negócio (adapte os campos ao seu tema)
class Entidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campo1 = db.Column(db.String(150), nullable=False)  # ex.: titulo
    campo2 = db.Column(db.String(100), nullable=False)  # ex.: autor
    campo3 = db.Column(db.String(50))                   # ex.: isbn
```

---

## 6) Fábrica da aplicação e registro de blueprints

```python
# app.py
from flask import Flask
from config import Config
from extensions import db, login_manager
from models import Usuario
from blueprints.web import web_bp
from blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()  # para começar; em produção, use migrações (Alembic)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

A função `create_app` segue o padrão **application factory**; isso facilita testes e deploy.

---

## 7) Blueprint WEB: formulários e rotas HTML

### 7.1 Inicialização do blueprint e formulários

```python
# blueprints/web/__init__.py
from flask import Blueprint
web_bp = Blueprint("web", __name__, template_folder="../templates")
from . import routes  # noqa
```

```python
# blueprints/web/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistroForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirmar = PasswordField("Confirmar Senha", validators=[EqualTo("senha")])
    submit = SubmitField("Registrar")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")
```

### 7.2 Rotas HTML (login/registro/CRUD básico)

```python
# blueprints/web/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import web_bp
from .forms import LoginForm, RegistroForm
from extensions import db
from models import Usuario, Entidade

@web_bp.route("/")
def index():
    return render_template("layout.html")

@web_bp.route("/registro", methods=["GET", "POST"])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash("E-mail já cadastrado.", "warning")
            return redirect(url_for("web.registro"))
        u = Usuario(nome=form.nome.data, email=form.email.data)
        u.set_senha(form.senha.data)
        db.session.add(u)
        db.session.commit()
        flash("Conta criada. Faça login.", "success")
        return redirect(url_for("web.login"))
    return render_template("registro.html", form=form)

@web_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = Usuario.query.filter_by(email=form.email.data).first()
        if u and u.check_senha(form.senha.data):
            login_user(u)
            return redirect(url_for("web.lista"))
        flash("Credenciais inválidas.", "danger")
    return render_template("login.html", form=form)

@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.login"))

@web_bp.route("/entidades")
@login_required
def lista():
    q = request.args.get("q", "").strip()
    query = Entidade.query
    if q:
        # exemplo de busca simples por dois campos
        query = query.filter(
            (Entidade.campo1.ilike(f"%{q}%")) | (Entidade.campo2.ilike(f"%{q}%"))
        )
    itens = query.order_by(Entidade.id.desc()).all()
    return render_template("lista.html", itens=itens, busca=q)

@web_bp.route("/entidades/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        e = Entidade(
            campo1=request.form.get("campo1"),
            campo2=request.form.get("campo2"),
            campo3=request.form.get("campo3"),
        )
        db.session.add(e)
        db.session.commit()
        flash("Registro criado.", "success")
        return redirect(url_for("web.lista"))
    return render_template("editar.html", item=None)

@web_bp.route("/entidades/<int:pk>/editar", methods=["GET", "POST"])
@login_required
def editar(pk):
    e = Entidade.query.get_or_404(pk)
    if request.method == "POST":
        e.campo1 = request.form.get("campo1")
        e.campo2 = request.form.get("campo2")
        e.campo3 = request.form.get("campo3")
        db.session.commit()
        flash("Registro atualizado.", "success")
        return redirect(url_for("web.lista"))
    return render_template("editar.html", item=e)

@web_bp.route("/entidades/<int:pk>/excluir", methods=["POST"])
@login_required
def excluir(pk):
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
from flask import Blueprint
api_bp = Blueprint("api", __name__)
from . import routes  # noqa
```

```python
# blueprints/api/routes.py
from flask import jsonify, request, abort
from extensions import db
from models import Entidade
from . import api_bp

def to_dict(e: Entidade):
    return {"id": e.id, "campo1": e.campo1, "campo2": e.campo2, "campo3": e.campo3}

@api_bp.route("/entidades", methods=["GET"])
def api_listar():
    itens = Entidade.query.order_by(Entidade.id.desc()).all()
    return jsonify([to_dict(e) for e in itens]), 200

@api_bp.route("/entidades/<int:pk>", methods=["GET"])
def api_obter(pk):
    e = Entidade.query.get_or_404(pk)
    return jsonify(to_dict(e)), 200

@api_bp.route("/entidades", methods=["POST"])
def api_criar():
    dados = request.get_json(silent=True) or {}
    if not all(k in dados for k in ("campo1", "campo2")):
        abort(400, description="Campos obrigatórios: campo1, campo2")
    e = Entidade(campo1=dados["campo1"], campo2=dados["campo2"], campo3=dados.get("campo3"))
    db.session.add(e)
    db.session.commit()
    return jsonify(to_dict(e)), 201

@api_bp.route("/entidades/<int:pk>", methods=["PUT", "PATCH"])
def api_atualizar(pk):
    e = Entidade.query.get_or_404(pk)
    dados = request.get_json(silent=True) or {}
    e.campo1 = dados.get("campo1", e.campo1)
    e.campo2 = dados.get("campo2", e.campo2)
    e.campo3 = dados.get("campo3", e.campo3)
    db.session.commit()
    return jsonify(to_dict(e)), 200

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
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Projeto Flask</title>
  </head>
  <body>
    {% with mensagens = get_flashed_messages(with_categories=true) %}
      {% if mensagens %}
        <ul>
          {% for cat, msg in mensagens %}
            <li class="{{ cat }}">{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <main>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

`templates/login.html`:
```html
{% extends "layout.html" %}
{% block content %}
  <h2>Login</h2>
  <form method="POST">
    {{ csrf_token() }}
    <input name="email" type="email" placeholder="Email" required>
    <input name="senha" type="password" placeholder="Senha" required>
    <button type="submit">Entrar</button>
  </form>
  <p>Ainda não tem conta? <a href="{{ url_for('web.registro') }}">Registre-se</a></p>
{% endblock %}
```

`templates/registro.html`:
```html
{% extends "layout.html" %}
{% block content %}
  <h2>Registro</h2>
  <form method="POST">
    {{ csrf_token() }}
    <input name="nome" placeholder="Nome" required>
    <input name="email" type="email" placeholder="Email" required>
    <input name="senha" type="password" placeholder="Senha" required>
    <input name="confirmar" type="password" placeholder="Confirmar senha" required>
    <button type="submit">Criar conta</button>
  </form>
{% endblock %}
```

`templates/lista.html` e `templates/editar.html` podem seguir o padrão básico de formulários HTML exibidos pelas rotas do blueprint **web**.

> Para **formularização com Flask‑WTF e mensagens de erro mais ricas**, utilize classes `FlaskForm` no módulo `forms.py` e os padrões demonstrados no tutorial específico de Flask‑WTF (campos, validadores e CSRF).

---

## 10) Inicializar o banco e executar

Garanta que o servidor de banco (MySQL ou PostgreSQL) está rodando e que o usuário/DB existem. Em seguida:

Windows (PowerShell):
```powershell
$env:FLASK_APP="app:create_app"
$env:FLASK_ENV="development"
flask run
```

Linux/macOS (bash):
```bash
export FLASK_APP="app:create_app"
export FLASK_ENV="development"
flask run
```

Abra `http://127.0.0.1:5000/` no navegador para testar a camada web. Para a API, use `curl` ou Postman:

```bash
# listar
curl http://127.0.0.1:5000/api/entidades

# criar
curl -X POST -H "Content-Type: application/json"   -d '{"campo1":"Exemplo","campo2":"Autor","campo3":"Opcional"}'   http://127.0.0.1:5000/api/entidades
```

---

## 11) Boas práticas e próximos passos

Em produção, use HTTPS, variáveis de ambiente para segredos, migrações com **Alembic/Flask-Migrate**, e considere autenticação por token para a API. Para uploads, valide tipos e tamanhos, salve com `secure_filename` e, se possível, armazene em serviços externos (S3/GCS).

---

## Referência didática (Flask‑WTF, validação e CSRF)

A modelagem de formulários, a proteção CSRF e as práticas de renderização em Jinja2 seguem o tutorial dedicado de Flask‑WTF já fornecido ao curso. Consulte-o para revisar conceitos e expandir os formulários deste projeto.
