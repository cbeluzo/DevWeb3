# Tutorial de Autenticação com Flask-Login

Este guia vai te ensinar a proteger rotas e gerenciar o acesso de usuários em sua aplicação Flask, usando a extensão **Flask-Login**.

---

## 1. Instalação e Configuração

Primeiro, instale as bibliotecas necessárias.

```bash
pip install Flask-Login Werkzeug Flask-SQLAlchemy
```

Salve as dependências:
```bash
pip freeze > requirements.txt
```

### Estrutura do Projeto
```
/meu_projeto
|-- app.py
|-- /templates
|   |-- layout.html
|   |-- login.html
|   |-- registro.html
|   |-- perfil.html
```

### Configuração do `app.py`
```python
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-forte'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuração do gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Rota padrão para login
login_manager.login_message = 'Por favor, faça login para acessar esta página'
login_manager.login_message_category = 'warning'

# Modelo de Usuário
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Usuario('{self.nome}', '{self.email}')"

# Função de carregamento de usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()
```

---

## 2. Registro de Usuário

Crie a rota de registro. Sempre use `generate_password_hash()` antes de salvar a senha.

```python
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        hashed_senha = generate_password_hash(request.form['senha'], method='sha256')
        novo_usuario = Usuario(
            nome=request.form['nome'],
            email=request.form['email'],
            senha=hashed_senha
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')
```

**`templates/registro.html`**
```html
{% extends "layout.html" %}
{% block content %}
  <h2>Registro</h2>
  <form method="POST">
    <input type="text" name="nome" placeholder="Nome" required>
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="senha" placeholder="Senha" required>
    <button type="submit">Registrar</button>
  </form>
{% endblock %}
```

---

## 3. Login de Usuário

A rota de login verifica o e-mail e senha usando `check_password_hash`.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(email=request.form['email']).first()
        if usuario and check_password_hash(usuario.senha, request.form['senha']):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Email ou senha incorretos', 'danger')
    return render_template('login.html')
```

**`templates/login.html`**
```html
{% extends "layout.html" %}
{% block content %}
  <h2>Login</h2>
  <form method="POST">
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="senha" placeholder="Senha" required>
    <button type="submit">Entrar</button>
  </form>
{% endblock %}
```

---

## 4. Rota Protegida e Logout

```python
@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', usuario=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))
```

**`templates/perfil.html`**
```html
{% extends "layout.html" %}
{% block content %}
  <h2>Bem-vindo, {{ usuario.nome }}!</h2>
  <a href="{{ url_for('logout') }}">Sair</a>
{% endblock %}
```

---

## 5. Template Base com Flash Messages

**`templates/layout.html`**
```html
<!doctype html>
<html lang="pt-br">
  <head>
    <title>Flask-Login App</title>
  </head>
  <body>
    {% with mensagens = get_flashed_messages(with_categories=true) %}
      {% if mensagens %}
        <ul>
          {% for categoria, mensagem in mensagens %}
            <li class="{{ categoria }}">{{ mensagem }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </body>
</html>
```

---

✅ Agora o tutorial cobre **registro, login, logout e proteção de rotas** com explicações claras, templates organizados e exemplos funcionais.
