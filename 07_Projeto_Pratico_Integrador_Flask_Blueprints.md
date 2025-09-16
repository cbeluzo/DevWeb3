# Projeto Prático Integrador com Flask e Blueprints
## (Flask-WTF, Autenticação, CSRF, API RESTful, MySQL/PostgreSQL)

Este projeto consolida os conceitos estudados: **Flask, Flask-WTF, CSRF, autenticação com Flask-Login, API RESTful, persistência em banco de dados relacional (MySQL ou PostgreSQL)** e agora também **organização modular com Blueprints**.

---

## 1. Introdução ao Projeto

Você deverá desenvolver uma aplicação web **completa e segura**, usando Flask, que inclua:

- Cadastro e login de usuários com **hash de senha**.
- Proteção de formulários com **CSRF** (Flask-WTF).
- CRUD completo de uma entidade principal (livros, produtos, alunos etc.).
- API RESTful com endpoints equivalentes ao CRUD.
- Persistência em banco de dados **MySQL** ou **PostgreSQL** via SQLAlchemy.
- Organização do código em **Blueprints** (módulos separados).
- Boas práticas de segurança (hash de senha, validação de dados, variáveis de ambiente).

---

## 2. Opções de Temas

Você pode escolher **um dos seguintes temas**:

- **Sistema de Gerenciamento de Livros**  
  Cadastro, listagem, edição, exclusão e busca de livros por título, autor ou ISBN.

- **Controle de Estoque para Loja de Roupas**  
  Cadastro de produtos, controle de estoque, ajuste de preços e registro de vendas.

- **Sistema de Reserva de Salas**  
  Cadastro de salas de reunião, reservas em horários diferentes e visualização de reservas.

- **Gerenciamento de Funcionários**  
  Cadastro e controle de funcionários, incluindo salários e cargos.

- **Cadastro de Pacientes para Clínica Médica**  
  Cadastro de pacientes, histórico médico, agendamento de consultas e prescrições.

- **Sistema de Gerenciamento de Tarefas**  
  Criação de listas de tarefas, conclusão e definição de prazos.

- **Sistema de Cadastro de Alunos e Notas**  
  Cadastro de alunos, lançamento de notas e geração de boletins.

- **Sistema de Aluguel de Carros**  
  Cadastro de veículos, registro de locações, controle de devoluções e histórico de clientes.

- **Gerenciamento de Produtos em uma Lanchonete**  
  Cadastro de produtos, controle de ingredientes e gerenciamento de pedidos.

- **Sistema de Gerenciamento de Projetos**  
  Cadastro de projetos, atribuição de tarefas e acompanhamento de progresso.

- **Sistema de Reservas para Restaurante**  
  Cadastro de mesas, reservas e visualização de disponibilidade.

- **Sistema de Cadastro de Clientes para Academia**  
  Cadastro de clientes, planos, treinos e pagamentos.

- **Sistema de Biblioteca Virtual**  
  Cadastro de usuários e livros, empréstimo e controle de devoluções.

- **Gerenciamento de Equipamentos para Manutenção**  
  Cadastro de equipamentos e histórico de manutenções.

- **Controle de Orçamentos para Empresa**  
  Cadastro de clientes, geração de orçamentos e controle de aprovação/execução.

> Caso queira, você pode propor outro tema, desde que siga o mesmo **modelo de CRUD + autenticação + API RESTful**.

---

## 3. Estrutura do Projeto

```
/meu_projeto
|-- app.py
|-- config.py
|-- models.py
|-- extensions.py          # inicialização de db, login_manager etc.
|-- /blueprints
|   |-- __init__.py
|   |-- web
|   |   |-- __init__.py
|   |   |-- routes.py      # rotas HTML (CRUD com Flask-WTF)
|   |   |-- forms.py
|   |-- api
|   |   |-- __init__.py
|   |   |-- routes.py      # rotas RESTful (JSON)
|-- /templates
|   |-- layout.html
|   |-- login.html
|   |-- registro.html
|   |-- lista.html
|   |-- editar.html
|-- /static
|   |-- css
|   |-- img
|-- /uploads
|-- requirements.txt
```

---

## 4. Código Base (Exemplos)

### 4.1 app.py
```python
from flask import Flask
from config import Config
from extensions import db, login_manager
from blueprints.web import web_bp
from blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # extensões
    db.init_app(app)
    login_manager.init_app(app)

    # blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

---

### 4.2 extensions.py
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "web.login"  # rota protegida
```

---

### 4.3 blueprints/web/__init__.py
```python
from flask import Blueprint

web_bp = Blueprint("web", __name__, template_folder="../templates")

from . import routes
```

---

### 4.4 blueprints/web/routes.py
```python
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, RegistroForm
from models import db, Usuario

@web_bp.route("/")
def index():
    return render_template("layout.html")

@web_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            login_user(usuario)
            return redirect(url_for("web.index"))
        flash("Credenciais inválidas", "danger")
    return render_template("login.html", form=form)

@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.login"))
```

---

### 4.5 blueprints/api/__init__.py
```python
from flask import Blueprint

api_bp = Blueprint("api", __name__)

from . import routes
```

---

### 4.6 blueprints/api/routes.py
```python
from flask import jsonify, request
from models import db, Entidade
from . import api_bp

@api_bp.route("/entidades", methods=["GET"])
def listar_entidades():
    entidades = Entidade.query.all()
    return jsonify([{"id": e.id, "campo1": e.campo1, "campo2": e.campo2} for e in entidades])

@api_bp.route("/entidades", methods=["POST"])
def criar_entidade():
    dados = request.get_json()
    entidade = Entidade(campo1=dados["campo1"], campo2=dados["campo2"])
    db.session.add(entidade)
    db.session.commit()
    return jsonify({"mensagem": "Entidade criada com sucesso"}), 201
```

---

## 5. Critérios de Avaliação

- **Funcionalidade (40%)**: CRUD completo + login + API RESTful.  
- **Boas práticas (30%)**: segurança (hash, CSRF), organização do código em Blueprints, uso de variáveis de ambiente.  
- **Banco de dados (20%)**: persistência correta em MySQL/PostgreSQL.  
- **Documentação (10%)**: README claro, com instruções de execução e screenshots.  

---

✅ Este projeto prático garante a integração de todos os conhecimentos estudados, aplicados a um caso realista de sistema de gestão, com **arquitetura modular em Blueprints**.
