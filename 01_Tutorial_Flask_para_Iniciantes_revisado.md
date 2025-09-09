# Tutorial Flask para Iniciantes

Este guia prático vai te ajudar a construir sua primeira aplicação web com **Flask** de forma simples e intuitiva, usando o **PyCharm**.

---

## 1. Preparando o Ambiente com PyCharm

O PyCharm é uma IDE (ambiente de desenvolvimento integrado) com excelente suporte para Python e Flask.

1. **Crie um Novo Projeto no PyCharm:**  
   - Abra o PyCharm.  
   - Clique em **"New Project"**.  
   - Dê um nome ao seu projeto (ex: `flask_iniciante`).  
   - Na seção **"Interpreter"**, selecione **"New environment using Virtualenv"**.  
   - O PyCharm criará e configurará o ambiente virtual automaticamente.  
   - Clique em **"Create"**.

2. **Instale o Flask:**  
   - No PyCharm, abra o **Terminal** (parte inferior da tela).  
   - O ambiente virtual já estará ativo.  
   - Digite:  
     ```bash
     pip install flask
     ```

3. **Salve as Dependências:**  
   - Para registrar as dependências em um arquivo `requirements.txt`, execute:  
     ```bash
     pip freeze > requirements.txt
     ```

---

## 2. Sua Primeira Aplicação Flask

Agora vamos criar um arquivo simples para sua primeira aplicação.

1. No painel do projeto, clique com o botão direito na pasta principal → **New > Python File**.  
2. Nomeie o arquivo como `app.py`.  
3. Insira o seguinte código:

```python
from flask import Flask

# Cria uma instância da aplicação Flask
app = Flask(__name__)

# Define uma rota para a página inicial
@app.route('/')
def home():
    return 'Olá, mundo! Esta é minha primeira aplicação Flask.'

# Rota com parâmetro dinâmico
@app.route('/usuario/<nome>')
def saudar_usuario(nome):
    return f'Olá, {nome}! Bem-vindo à nossa aplicação.'

# Executa a aplicação em modo de desenvolvimento
if __name__ == '__main__':
    app.run(debug=True)
```

4. **Rodar a aplicação:**  
   - Clique com o botão direito em `app.py` → **Run 'app'**.  
   - O servidor ficará disponível em:  
     ```
     http://127.0.0.1:5000/
     ```

### Testando no Navegador
- `http://127.0.0.1:5000/` → mostra: **"Olá, mundo!..."**  
- `http://127.0.0.1:5000/usuario/Ana` → mostra: **"Olá, Ana!..."**

---

## 3. Entendendo Rotas e Views

As **rotas** são como endereços que definem como a aplicação responde a URLs específicas.  
- O `@app.route()` é um **decorador** que liga uma URL a uma função Python.  
- A função associada é chamada de **view**: ela processa a requisição e retorna a resposta.

### Parâmetros de URL
É possível criar rotas **dinâmicas**:

| Tipo     | Exemplo de rota | Resultado esperado |
|----------|----------------|--------------------|
| `string` | `/post/<string:titulo>` | Recebe texto |
| `int`    | `/post/<int:id>` | Recebe número inteiro |
| `float`  | `/produto/<float:preco>` | Recebe número decimal |
| `path`   | `/arquivo/<path:caminho>` | Recebe um caminho completo |

Exemplo:
```python
@app.route('/quadrado/<int:num>')
def quadrado(num):
    return f"O quadrado de {num} é {num*num}"
```

---

## 4. Trabalhando com Métodos HTTP

Por padrão, as rotas aceitam apenas `GET`.  
Se quiser aceitar outros métodos como `POST`, especifique:

```python
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'Processando login...'
    else:
        return 'Página de login'
```

Isso é muito usado para **formulários**.

---

## 5. Renderizando Templates com Jinja2

O Flask utiliza o **Jinja2** para separar lógica (Python) da apresentação (HTML).

### Estrutura do Projeto
```
/meu_projeto
|-- app.py
|-- /templates
|   |-- index.html
|   |-- layout.html
```

### Exemplo de Template Base (`layout.html`)
```html
<!doctype html>
<html lang="pt-br">
  <head>
    <title>{{ titulo }}</title>
  </head>
  <body>
    <h1>{{ titulo }}</h1>
    {% block conteudo %}{% endblock %}
  </body>
</html>
```

### Página com Conteúdo (`index.html`)
```html
{% extends "layout.html" %}
{% block conteudo %}
  <p>Bem-vindo ao Flask, {{ usuario }}!</p>
{% endblock %}
```

### Alterando `app.py`
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html", titulo="Minha Página Inicial", usuario="Carlos")
```

Agora, ao acessar `http://127.0.0.1:5000/`, você verá a página HTML renderizada.
