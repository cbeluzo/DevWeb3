# Tutorial de Blueprints no Flask

Os **Blueprints** permitem organizar uma aplicação Flask em múltiplos módulos, tornando-a mais modular, reutilizável e fácil de manter.

---

## 1. O que são Blueprints?

Blueprints, ou "plantas", são componentes que permitem dividir uma aplicação Flask em **mini-aplicativos modulares**.  
Eles não funcionam sozinhos — precisam ser registrados na aplicação principal.

Vantagens:
- **Modularidade**: cada funcionalidade tem seu próprio diretório.  
- **Reutilização**: módulos podem ser usados em outros projetos.  
- **Organização**: separação clara entre diferentes partes do sistema.  
- **Manutenção**: facilita localizar e alterar funcionalidades específicas.  

---

## 2. Estrutura do Projeto

Crie as pastas e arquivos conforme o esquema abaixo:

```
/meu_projeto
|-- run.py               # Script principal para iniciar a aplicação
|-- /app
|   |-- __init__.py      # Criação da aplicação e registro dos blueprints
|   |-- /auth
|   |   |-- __init__.py  # Criação do Blueprint 'auth'
|   |   |-- routes.py    # Rotas de autenticação
|   |   |-- /templates/auth/
|   |   |   |-- login.html
|   |   |   |-- registro.html
|   |-- /main
|   |   |-- __init__.py  # Criação do Blueprint 'main'
|   |   |-- routes.py    # Rotas principais
|   |   |-- /templates/main/
|   |   |   |-- home.html
|   |-- /templates       # Templates globais
|   |   |-- layout.html
|-- requirements.txt
```

---

## 3. Criando e Registrando Blueprints

### Passo 1: Script de Execução (`run.py`)

Arquivo que inicia a aplicação.

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

---

### Passo 2: Aplicação Principal (`app/__init__.py`)

Aqui criamos a aplicação Flask e registramos os blueprints.

```python
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uma-chave-secreta-forte'

    # Importa e registra o Blueprint 'main'
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Importa e registra o Blueprint 'auth' com prefixo de URL
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
```

---

### Passo 3: Blueprint de Autenticação (`app/auth/__init__.py`)

```python
from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates')

from . import routes
```

**Rotas (`app/auth/routes.py`)**
```python
from flask import render_template, redirect, url_for
from . import auth

@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/registro')
def registro():
    return render_template('auth/registro.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('main.index'))
```

---

### Passo 4: Blueprint Principal (`app/main/__init__.py`)

```python
from flask import Blueprint

main = Blueprint('main', __name__, template_folder='templates')

from . import routes
```

**Rotas (`app/main/routes.py`)**
```python
from flask import render_template
from . import main

@main.route('/')
def index():
    return render_template('main/home.html')

@main.route('/sobre')
def sobre():
    return "<h2>Página Sobre</h2><p>Exemplo de rota no Blueprint principal.</p>"
```

---

## 4. Templates

### Template Base (`app/templates/layout.html`)
```html
<!doctype html>
<html lang="pt-br">
  <head>
    <title>{% block title %}Flask App{% endblock %}</title>
  </head>
  <body>
    <header>
      <a href="{{ url_for('main.index') }}">Início</a> |
      <a href="{{ url_for('main.sobre') }}">Sobre</a> |
      <a href="{{ url_for('auth.login') }}">Login</a> |
      <a href="{{ url_for('auth.registro') }}">Registro</a>
    </header>
    <main>
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

### Template Home (`app/main/templates/main/home.html`)
```html
{% extends "layout.html" %}
{% block title %}Página Inicial{% endblock %}
{% block content %}
  <h1>Bem-vindo à aplicação com Blueprints!</h1>
{% endblock %}
```

### Template Login (`app/auth/templates/auth/login.html`)
```html
{% extends "layout.html" %}
{% block title %}Login{% endblock %}
{% block content %}
  <h2>Login</h2>
  <form>
    <input type="email" placeholder="Email">
    <input type="password" placeholder="Senha">
    <button type="submit">Entrar</button>
  </form>
{% endblock %}
```

---

✅ Agora o tutorial explica claramente **como criar, registrar e usar Blueprints**, com estrutura organizada e exemplos funcionais.
