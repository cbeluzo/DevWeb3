# Objetivos e justificativa (o que será feito e por quê)
Formulários HTML “puros” exigem muito código repetitivo para validar campos, exibir erros e proteger contra ataques CSRF. O **Flask‑WTF** abstrai esses detalhes ao:
- **Definir formulários como classes Python**, facilitando reutilização e testes.
- **Aplicar validação declarativa** com validadores prontos e personalizados.
- **Proteger contra CSRF** por padrão, inserindo e validando o token de forma automática.
- **Integrar-se ao Jinja2** de modo a renderizar campos e mensagens de erro com consistência.

O ganho é acelerar o desenvolvimento, reduzir erros e padronizar a interface do usuário.

---

# Conceitos fundamentais
**WTForms** é uma biblioteca de formulários orientada a objetos (campos, validadores, mensagens de erro). **Flask‑WTF** fornece a cola entre WTForms e Flask: _hooks_ de requisição, integração CSRF, _helpers_ para `validate_on_submit()` e uma classe base `FlaskForm`.

**CSRF (Cross‑Site Request Forgery)** é um ataque em que um site malicioso tenta forçar um navegador autenticado a enviar requisições não intencionadas. O **token CSRF** evita isso: cada formulário inclui um token secreto verificado no servidor.

**Validadores** são funções/objetos que verificam dados de campos. Exemplos: `DataRequired`, `Email`, `Length`, `EqualTo`, além de **validadores customizados** via exceção `ValidationError`.

---

# Preparação do projeto
Estrutura mínima sugerida:
```
/meu_projeto
|-- app.py
|-- forms.py
|-- /templates
|   |-- layout.html
|   |-- contato.html
|   |-- macros.html
|-- /uploads          # diretório para armazenar arquivos enviados
|-- requirements.txt
```

Instalação:
```bash
pip install Flask Flask-WTF WTForms email-validator
```
> `email-validator` melhora a verificação de e-mails (`EmailField`).

Configuração básica (`app.py`):
```python
# Importa a classe principal do Flask, usada para criar a aplicação web
from flask import Flask

# Importa a extensão do Flask-WTF responsável pela proteção contra ataques CSRF
from flask_wtf import CSRFProtect

# Cria a instância da aplicação Flask
# Esta será a base para definir rotas, configurações e iniciar o servidor
app = Flask(__name__)

# Define a chave secreta da aplicação.
# Ela é usada para:
#   - Assinar cookies de sessão
#   - Gerar e validar tokens CSRF
# IMPORTANTE: em produção, essa chave deve ser forte e guardada em variáveis de ambiente.
app.config['SECRET_KEY'] = 'uma-chave-secreta-forte'  # mude em produção

# Ativa a proteção global contra CSRF em toda a aplicação Flask.
# Com isso, qualquer formulário processado pelo Flask-WTF terá automaticamente
# um token CSRF incluído e validado, aumentando a segurança contra requisições maliciosas.
csrf = CSRFProtect(app)

```

- SECRET_KEY → chave usada para segurança interna do Flask (sessão + CSRF).

- CSRFProtect(app) → habilita proteção automática em todos os formulários HTML.

- Esse é o mínimo necessário para garantir que formulários Flask-WTF sejam seguros.

---

## 1. O que é **Flask-WTF**

O **Flask-WTF** é uma extensão do Flask que integra o **WTForms** (biblioteca para manipulação de formulários em Python) ao framework.
Ele facilita a criação e validação de formulários HTML, trazendo recursos como:

* Criação de formulários como classes Python.
* Validação automática de campos.
* Proteção contra ataques **CSRF** (Cross-Site Request Forgery).
* Integração simples com `render_template` para gerar formulários no HTML.

Exemplo de formulário com Flask-WTF:

```python
# Importa a classe base para criação de formulários com Flask-WTF
from flask_wtf import FlaskForm

# Importa tipos de campos que podem ser usados no formulário
from wtforms import StringField, PasswordField, SubmitField

# Importa validadores prontos do WTForms
from wtforms.validators import DataRequired, Email

# Define uma classe de formulário chamada LoginForm
# Cada atributo corresponde a um campo do formulário HTML
class LoginForm(FlaskForm):
    
    # Campo de texto simples para email
    # Validadores aplicados:
    #   - DataRequired: o campo não pode ficar vazio
    #   - Email: exige um formato válido de email (ex: usuario@dominio.com)
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Campo do tipo senha (input type="password")
    # Validador:
    #   - DataRequired: o campo não pode ficar vazio
    senha = PasswordField("Senha", validators=[DataRequired()])

    # Botão de envio do formulário
    submit = SubmitField("Entrar")

```

- FlaskForm → base para todos os formulários no Flask-WTF.

- StringField, PasswordField, SubmitField → tipos de campo.

- Validadores (DataRequired, Email) → regras aplicadas automaticamente quando chamamos form.validate_on_submit().

- Esse formulário gera, no HTML, inputs prontos para email e senha, já com validação embutida.
---

## 2. O que é **CSRFProtect**

O **CSRFProtect** é o mecanismo de segurança oferecido pelo Flask-WTF.
Ele protege a aplicação contra **ataques de falsificação de requisição entre sites** (Cross-Site Request Forgery).
Sempre que um formulário é enviado, o Flask-WTF inclui um **token secreto** no HTML. Esse token precisa ser enviado de volta para que o servidor aceite a requisição.

Sem esse recurso, um atacante poderia criar uma página falsa que dispara requisições maliciosas para o servidor do usuário autenticado.

Ativação típica no `app.py`:

```python
# Importa a classe principal do Flask, necessária para criar a aplicação web
from flask import Flask

# Importa a extensão responsável pela proteção contra ataques CSRF
# (Cross-Site Request Forgery), que é fornecida pelo Flask-WTF
from flask_wtf.csrf import CSRFProtect

# Cria a instância principal da aplicação Flask
app = Flask(__name__)

# Define a chave secreta usada pelo Flask para:
#   - Assinar cookies de sessão
#   - Gerar e validar os tokens CSRF nos formulários
# IMPORTANTE: em produção, essa chave deve ser forte e nunca ficar fixa no código;
# deve ser carregada de variáveis de ambiente ou de um cofre de segredos.
app.config["SECRET_KEY"] = "uma_chave_secreta"

# Ativa a proteção global contra CSRF na aplicação
# A partir daqui, todo formulário HTML que usar Flask-WTF
# terá automaticamente um token CSRF incluído e validado
csrf = CSRFProtect(app)

```

- SECRET_KEY → chave usada para segurança interna (sessão e tokens CSRF).

- CSRFProtect(app) → habilita proteção automática contra ataques de falsificação de requisições.

- Assim, qualquer formulário criado com Flask-WTF já terá token CSRF obrigatório para ser aceito.

---

## 3. Funções auxiliares do Flask

Essas funções são importadas de `flask` e são usadas frequentemente junto com formulários:

* **`render_template`**: renderiza um arquivo HTML e passa variáveis Python para dentro do template.

  ```python
  return render_template("login.html", form=form)
  ```

* **`redirect`**: redireciona o usuário para outra rota após uma ação (ex.: login bem-sucedido).

  ```python
  return redirect(url_for("dashboard"))
  ```

* **`url_for`**: gera URLs dinâmicas baseadas no nome da função de rota.

  ```python
  url_for("login")   # gera "/login"
  ```

* **`flash`**: envia mensagens temporárias para o usuário (ex.: "Login inválido"). Essas mensagens são armazenadas na sessão e exibidas no template.

  ```python
  flash("Usuário ou senha inválidos", "error")
  ```

* **`request`**: acessa os dados da requisição HTTP (GET, POST, headers, etc.).

  ```python
  request.form["email"]   # lê um campo enviado por formulário
  ```

---

## 4. Exemplo Completo

### Rota em Flask

```python
# Define a rota /login que aceita os métodos GET (mostrar formulário)
# e POST (enviar formulário para validação)
@app.route("/login", methods=["GET", "POST"])
def login():
    # Cria uma instância do formulário de login
    form = LoginForm()

    # Verifica se o formulário foi submetido via POST
    # e se todos os validadores passaram (inclusive o token CSRF)
    if form.validate_on_submit():  # valida CSRF + campos

        # Exemplo de validação "na mão":
        # confere se email e senha correspondem a valores fixos
        if form.email.data == "admin@email.com" and form.senha.data == "123":
            # Se for válido → mensagem de sucesso
            flash("Login realizado com sucesso!", "success")

            # Redireciona o usuário para a rota 'dashboard'
            return redirect(url_for("dashboard"))
        else:
            # Caso contrário, mostra mensagem de erro
            flash("Credenciais inválidas!", "error")

    # Se for requisição GET ou se houver erros de validação,
    # renderiza o template do formulário novamente
    return render_template("login.html", form=form)

```

- GET → mostra o formulário de login.

- POST → processa os dados enviados.

- form.validate_on_submit() → valida campos e token CSRF.

- Se login for válido → flash com sucesso + redirect para dashboard.

- Se inválido → flash com erro e reexibe o formulário.

### Template HTML (`login.html`)

```html
<form method="POST">
    {# Inclui automaticamente campos ocultos do Flask-WTF,
       incluindo o token CSRF (proteção contra ataques Cross-Site Request Forgery) #}
    {{ form.hidden_tag() }}

    {# Label e campo de input para email #}
    {{ form.email.label }} {{ form.email }}

    {# Label e campo de input para senha (password) #}
    {{ form.senha.label }} {{ form.senha }}

    {# Botão de envio do formulário #}
    {{ form.submit }}
</form>

{# Bloco que exibe mensagens flash enviadas pelo backend (flash()) #}
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
    {# Cada mensagem terá uma "categoria" (ex.: success, error),
       que pode ser usada como classe CSS para estilizar #}
    <p class="{{ category }}">{{ message }}</p>
  {% endfor %}
{% endwith %}

```

- form.hidden_tag() → insere o token CSRF e outros campos ocultos necessários.

- form.email, form.senha, form.submit → representam os campos definidos em LoginForm.

- get_flashed_messages(with_categories=True) → recupera mensagens enviadas pelo servidor via flash().

- category → permite estilizar mensagens (ex.: success em verde, error em vermelho).

---

## 5. Upload de Arquivos

Além de formulários comuns, o Flask-WTF permite criar **formularios de upload de arquivos**.

* **Bibliotecas usadas:**

  * `os` → manipula diretórios e arquivos.
  * `secure_filename` (Werkzeug) → garante nomes de arquivo seguros.
  * `send_from_directory` (Flask) → envia arquivos de uma pasta do servidor.

* **Formulário para upload (`forms.py`)**:

```python
# Importa a classe base para criação de formulários com Flask-WTF
from flask_wtf import FlaskForm

# Importa tipos de campo e validadores específicos para upload de arquivos
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Importa o tipo de campo para botão de envio
from wtforms import SubmitField


# Define o formulário de upload
class UploadForm(FlaskForm):

    # Campo do tipo "arquivo" (input type="file")
    # Validadores aplicados:
    #   - FileRequired: exige que o usuário selecione um arquivo
    #   - FileAllowed: restringe os tipos de arquivo aceitos
    #       neste caso: imagens (jpg, png), PDF e TXT
    arquivo = FileField(
        "Selecione um arquivo",
        validators=[
            FileRequired(),
            FileAllowed(
                ["jpg", "png", "pdf", "txt"],
                "Apenas imagens, PDF ou TXT são permitidos!"
            )
        ]
    )

    # Botão de envio do formulário
    submit = SubmitField("Enviar")

```

- FileField → cria um campo de upload de arquivo.

- FileRequired → impede envio vazio.

- FileAllowed → restringe extensões aceitas (nesse caso: imagens, PDF e TXT).

- SubmitField → cria o botão de envio.

* **Rota para upload (`app.py`)**:

```python
import os
from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from forms import UploadForm

# Cria a aplicação Flask
app = Flask(__name__)

# Chave secreta necessária para o uso do Flask-WTF (CSRF, sessão, etc.)
app.config["SECRET_KEY"] = "uma_chave_segura"

# Define a pasta onde os arquivos enviados serão armazenados
# Aqui usamos o diretório atual do projeto + subpasta "uploads"
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")

# Se a pasta de uploads não existir, cria automaticamente
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ---------------------------
# Rota de upload de arquivos
# ---------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    # Cria uma instância do formulário de upload
    form = UploadForm()

    # Verifica se o formulário foi enviado e se os validadores passaram
    if form.validate_on_submit():
        # Obtém o objeto FileStorage (arquivo enviado)
        arquivo = form.arquivo.data

        # Gera um nome de arquivo seguro (remove caracteres perigosos)
        nome_seguro = secure_filename(arquivo.filename)

        # Monta o caminho completo onde o arquivo será salvo
        caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)

        # Salva o arquivo no servidor
        arquivo.save(caminho)

        # Envia uma mensagem de sucesso para o usuário
        flash("Arquivo enviado com sucesso!", "success")

        # Redireciona para a rota de download para exibir o arquivo
        return redirect(url_for("download", nome=nome_seguro))

    # Se for GET ou se houver erro de validação, renderiza o formulário novamente
    return render_template("upload.html", form=form)

# ---------------------------
# Rota de download/exibição
# ---------------------------
@app.route("/uploads/<nome>")
def download(nome):
    # Retorna o arquivo solicitado a partir da pasta UPLOAD_FOLDER
    # Se for imagem ou PDF, o navegador tenta abrir diretamente
    # Se for outro tipo, o navegador pode oferecer o download
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome)
```

* **Template de upload (`upload.html`)**:

```html
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    {{ form.arquivo.label }} {{ form.arquivo }} <br>
    {{ form.submit }}
</form>

{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
    <p style="color: green;">{{ message }}</p>
  {% endfor %}
{% endwith %}
```

- O usuário acessa /upload → formulário é exibido.

- Ao enviar, o UploadForm valida se o arquivo é permitido.

- O nome do arquivo é higienizado com secure_filename.

- O arquivo é salvo na pasta uploads/.

- O usuário é redirecionado para /uploads/<nome>, onde pode visualizar ou baixar o arquivo.

---

## 6. Validadores do WTForms

O **WTForms** fornece validadores que garantem consistência dos dados:

* **`DataRequired`**: exige que o campo não esteja vazio.

  ```python
  nome = StringField("Nome", validators=[DataRequired()])
  ```

* **`Email`**: valida formato de e-mail.

  ```python
  email = StringField("Email", validators=[Email()])
  ```

* **`Length`**: restringe o tamanho do texto.

  ```python
  senha = PasswordField("Senha", validators=[Length(min=6)])
  ```

* **`EqualTo`**: exige igualdade entre dois campos.

  ```python
  confirmar = PasswordField("Confirmar Senha", validators=[EqualTo("senha")])
  ```

---

## 7. Fluxo Completo

1. Usuário acessa `/login` → envia email e senha.
2. O Flask-WTF valida os dados (com `DataRequired`, `Email`, etc.).
3. Se válido → redireciona com `redirect(url_for(...))`.
4. Usuário acessa `/upload` → envia um arquivo.
5. Arquivo é validado (`FileRequired`, `FileAllowed`).
6. Nome do arquivo é normalizado com `secure_filename`.
7. Arquivo é salvo em `/uploads`.
8. Usuário pode baixar o arquivo em `/uploads/<nome>`.


