# Tutorial Flask‑WTF: Formulários, Validação e Uploads

Este tutorial apresenta, de forma didática, como construir formulários web robustos no Flask usando **Flask‑WTF** (integração do **WTForms** com Flask). 

O foco é explicar o _porquê_ de cada etapa, introduzir conceitos essenciais (campos, validadores, CSRF), mostrar a integração com _views_ e _templates_, e fechar com um caso completo de **upload de arquivos** com boas práticas de segurança.

---

## 1. Objetivos e justificativa (o que será feito e por quê)
Formulários HTML “puros” exigem muito código repetitivo para validar campos, exibir erros e proteger contra ataques CSRF. O **Flask‑WTF** abstrai esses detalhes ao:
- **Definir formulários como classes Python**, facilitando reutilização e testes.
- **Aplicar validação declarativa** com validadores prontos e personalizados.
- **Proteger contra CSRF** por padrão, inserindo e validando o token de forma automática.
- **Integrar-se ao Jinja2** de modo a renderizar campos e mensagens de erro com consistência.

O ganho é acelerar o desenvolvimento, reduzir erros e padronizar a interface do usuário.

---

## 2. Conceitos fundamentais
**WTForms** é uma biblioteca de formulários orientada a objetos (campos, validadores, mensagens de erro). **Flask‑WTF** fornece a cola entre WTForms e Flask: _hooks_ de requisição, integração CSRF, _helpers_ para `validate_on_submit()` e uma classe base `FlaskForm`.

**CSRF (Cross‑Site Request Forgery)** é um ataque em que um site malicioso tenta forçar um navegador autenticado a enviar requisições não intencionadas. O **token CSRF** evita isso: cada formulário inclui um token secreto verificado no servidor.

**Validadores** são funções/objetos que verificam dados de campos. Exemplos: `DataRequired`, `Email`, `Length`, `EqualTo`, além de **validadores customizados** via exceção `ValidationError`.

---

## 3. Preparação do projeto
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
# Importa a classe principal do Flask para criar a aplicação web
from flask import Flask

# Importa a extensão que protege contra ataques CSRF (Cross-Site Request Forgery)
from flask_wtf import CSRFProtect

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Define a chave secreta usada internamente pelo Flask e pelo Flask-WTF.
# Essa chave é necessária para:
#   - assinar cookies de sessão
#   - gerar tokens CSRF
# OBS: em produção, use uma chave forte e segura, armazenada em variáveis de ambiente.
app.config['SECRET_KEY'] = 'uma-chave-secreta-forte'  # mude em produção

# Ativa a proteção contra CSRF em toda a aplicação.
# Isso garante que todos os formulários HTML que usam Flask-WTF incluam e validem o token CSRF automaticamente.
csrf = CSRFProtect(app)

```

---

## 4. Definindo formulários com Flask‑WTF
Crie `forms.py` com campos e validadores. Abaixo um **formulário de contato** completo (texto + seleção + e-mail), além de um **validador customizado** de exemplo:

```python
# forms.py
# Importa a classe base FlaskForm, usada para criar formulários em Flask-WTF
from flask_wtf import FlaskForm

# Importa diferentes tipos de campos que podem ser usados em um formulário
from wtforms import StringField, TextAreaField, EmailField, PasswordField, BooleanField, SelectField, FileField

# Importa validadores prontos do WTForms
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

# Função de validação personalizada.
# É chamada automaticamente pelo WTForms se incluída na lista de validadores do campo.
def validar_nome(form, field):
    # Verifica se o nome informado tem menos de 2 caracteres válidos (após remover espaços extras).
    if len(field.data.strip()) < 2:
        # Se inválido, gera uma exceção que interrompe a validação e mostra a mensagem ao usuário.
        raise ValidationError('Informe um nome válido (>= 2 caracteres).')

# Classe que define um formulário de contato.
# Cada atributo corresponde a um campo que aparecerá no HTML.
class ContatoForm(FlaskForm):

    # Campo de texto simples (input type="text").
    # Validadores aplicados:
    #   - DataRequired: campo não pode ser vazio
    #   - Length: exige entre 3 e 50 caracteres
    #   - validar_nome: função customizada definida acima
    nome = StringField(
        'Nome',
        validators=[
            DataRequired(message='Nome é obrigatório'),
            Length(min=3, max=50, message='Nome deve ter entre 3 e 50 caracteres'),
            validar_nome
        ]
    )

    # Campo específico para emails (input type="email").
    # Validadores:
    #   - DataRequired: não pode estar vazio
    #   - Email: verifica formato válido de email
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='Email é obrigatório'),
            Email(message='Informe um email válido')
        ]
    )

    # Campo do tipo select (caixa de seleção).
    # Exibe opções fixas para o usuário escolher.
    assunto = SelectField(
        'Assunto',
        choices=[
            ('suporte', 'Suporte Técnico'),
            ('vendas', 'Informações de Vendas'),
            ('outro', 'Outro Assunto')
        ]
    )

    # Campo de área de texto (textarea).
    # Validadores:
    #   - DataRequired: mensagem obrigatória
    #   - Length: exige pelo menos 10 caracteres
    mensagem = TextAreaField(
        'Mensagem',
        validators=[
            DataRequired(message='Mensagem é obrigatória'),
            Length(min=10, message='Mensagem deve ter pelo menos 10 caracteres')
        ]
    )

```

Esse ContatoForm é típico em páginas de fale conosco ou suporte, combinando validadores prontos (DataRequired, Email, Length) com um validador customizado (validar_nome).


Observações didáticas: cada campo encapsula **rótulo**, **dado submetido**, **lista de validadores** e **erros**. As mensagens de erro ficam disponíveis em `form.campo.errors` e são renderizadas no template.

---

## 5. Rotas (views) com validação no servidor
A lógica típica é: exibir o formulário via `GET` e processar via `POST`. Use `validate_on_submit()` para acionar a validação apenas quando o método for `POST` e os dados/CSRF forem válidos. O fluxo dessa rota é:
1) Usuário acessa /contato (GET) → formulário é exibido.
2) Usuário envia os dados (POST).
3) Flask-WTF valida os campos → se houver erro, formulário é reexibido.
4) Se estiver válido → mensagem de sucesso (flash) e redirecionamento para /.

```python
# app.py (continuação)
# Importa funções utilitárias do Flask
from flask import render_template, redirect, url_for, flash, request

# Importa o formulário de contato definido em forms.py
from forms import ContatoForm

# Rota principal ("/")
@app.route('/')
def home():
    # Renderiza o template "layout.html" (página inicial)
    return render_template('layout.html')

# Rota para exibir e processar o formulário de contato
# Aceita requisições GET (exibir o formulário) e POST (enviar dados)
@app.route('/contato', methods=['GET', 'POST'])
def contato():
    # Instancia o formulário
    form = ContatoForm()

    # Verifica se a requisição é POST e se os dados são válidos
    if form.validate_on_submit():
        # Se válido, acessa os dados dos campos
        nome = form.nome.data
        email = form.email.data
        assunto = form.assunto.data
        mensagem = form.mensagem.data

        # Aqui poderia ser feita alguma ação com os dados:
        # - enviar email
        # - salvar em banco de dados
        # - registrar em log
        # Por enquanto é apenas um placeholder
        # TODO: enviar email, persistir em DB, etc.

        # Exibe uma mensagem de sucesso ao usuário
        flash('Mensagem enviada com sucesso!', 'success')

        # Redireciona o usuário de volta para a página inicial
        return redirect(url_for('home'))

    # Se for uma requisição GET ou se houver erros de validação,
    # o formulário é renderizado novamente (com mensagens de erro, se houver).
    return render_template('contato.html', form=form)

```

---

## 6. Templates Jinja2 e macros de renderização
Em `templates/layout.html`, defina um _layout_ base simples e um bloco para mensagens _flash_ e conteúdo da página:

Esse arquivo funciona como template base.
Outros templates (ex.: contato.html) irão herdar dele usando {% extends "layout.html" %}.
O conteúdo da página será colocado dentro do bloco content.
As mensagens de flash aparecerão no topo automaticamente (útil para feedback de formulários).

```html
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <title>Exemplo Flask-WTF</title>

    <!-- Configuração para responsividade em dispositivos móveis -->
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>

    <!-- Bloco que exibe mensagens "flash" vindas do Flask -->
    {% with mensagens = get_flashed_messages(with_categories=true) %}
      {% if mensagens %}
        <ul>
          <!-- Percorre todas as mensagens exibindo como <li> -->
          {% for categoria, msg in mensagens %}
            <!-- "categoria" pode ser usada como classe CSS (ex: success, error) -->
            <li class="{{ categoria }}">{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <!-- Área principal da página -->
    <main>
      <!-- Espaço reservado para inserir conteúdo específico de cada template -->
      {% block content %}{% endblock %}
    </main>

  </body>
</html>

```

**Macros**

Esse macro evita repetir código HTML em cada campo.
Todos os campos terão a mesma estrutura: label, input e mensagens de erro.
Pode-se alterar css_class para aplicar estilos diferentes (ex.: Bootstrap form-control).
Use **macros** para padronizar a renderização dos campos e exibir erros de forma consistente (`templates/macros.html`):

```html
{# 
  Macro para renderizar campos de formulário no Flask-WTF com consistência visual.
  Pode ser chamada em qualquer template com:
      {{ render_field(form.nome, placeholder="Digite seu nome") }}
#}

{% macro render_field(field, placeholder="", css_class="form-control") %}
  <div class="form-group">
    
    {# Exibe o label do campo (ex: "Nome", "Email") #}
    <label>{{ field.label }}</label>
    
    {# Renderiza o campo de formulário em si,
       aplicando classes CSS (ex: Bootstrap) e placeholder opcional #}
    {{ field(class=css_class, placeholder=placeholder) }}
    
    {# Se houver erros de validação, exibe a primeira mensagem de erro #}
    {% if field.errors %}
      <div class="error">
        {{ field.errors[0] }}
      </div>
    {% endif %}
  </div>
{% endmacro %}

```



Por fim, o template do formulário (`templates/contato.html`) estende o _layout_, inclui as _macros_ e **rende o token CSRF**:

```html
{% extends "layout.html" %}
{% from "macros.html" import render_field %}

{% block content %}
  <h1>Fale Conosco</h1>
  <form method="POST" action="{{ url_for('contato') }}">
    {{ form.csrf_token }}
    {{ render_field(form.nome, placeholder="Seu nome completo") }}
    {{ render_field(form.email, placeholder="seu@email.com") }}
    {{ render_field(form.assunto) }}
    {{ render_field(form.mensagem, placeholder="Descreva sua solicitação") }}
    <button type="submit">Enviar</button>
  </form>
{% endblock %}
```

> O `form.csrf_token` é fundamental; sem ele, a validação CSRF falhará.

Fluxo de funcionamento desse template:

1) Ele estende layout.html, que já contém a estrutura HTML principal e área para mensagens flash.

2) Importa o macro render_field de macros.html, que padroniza a exibição de campos.

3) Renderiza cada campo do ContatoForm com labels, placeholders e mensagens de erro de validação.

4) Inclui o csrf_token para garantir segurança.

5) O botão envia os dados para a rota /contato, onde os dados são processados e validados.

---

## 7. Upload de arquivos com Flask‑WTF (FileField)
Para upload, use `FileField` e validadores específicos. Além disso, defina limites de tamanho e uma lista de extensões permitidas. No Flask puro, `MAX_CONTENT_LENGTH` rejeita requisições muito grandes logo na borda.

1) O Flask define uma pasta (UPLOAD_FOLDER) e tamanho máximo para uploads (MAX_CONTENT_LENGTH).

2) Apenas arquivos com extensões definidas em ALLOWED_EXTENSIONS são aceitos.

3) O formulário UploadForm usa FileField com validadores:

	FileRequired → impede envio vazio.

	FileAllowed → restringe os tipos de arquivo.

Configuração em `app.py`:

```python
import os
from werkzeug.utils import secure_filename

# Define a pasta onde os arquivos enviados serão salvos.
# Aqui usamos o caminho absoluto baseado na pasta atual do arquivo app.py.
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Define o tamanho máximo do arquivo permitido (em bytes).
# Neste caso: 16 MB (16 * 1024 * 1024 bytes).
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Conjunto de extensões de arquivos aceitas.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Cria automaticamente a pasta de uploads caso ela não exista.
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Função auxiliar que verifica se a extensão do arquivo é permitida.
def allowed_file(filename):
    # O nome do arquivo deve conter ponto (.) e a extensão final deve estar na lista ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

```

Form com `FileField` (em `forms.py`):

```python
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired

# Classe de formulário para upload de arquivos
class UploadForm(FlaskForm):
    # Campo do tipo FileField para seleção de arquivo
    arquivo = FileField(
        'Selecione um arquivo',
        validators=[
            # Garante que o usuário selecionou um arquivo
            FileRequired(message='Nenhum arquivo selecionado'),

            # Garante que o arquivo enviado tem uma extensão permitida
            FileAllowed(
                ['png', 'jpg', 'jpeg', 'gif', 'pdf'],
                message='Tipo de arquivo não permitido'
            )
        ]
    )

```

Rota de upload (em `app.py`):

Fluxo de funcionamento:

1) Usuário acessa /upload (GET) → formulário é exibido.

2) Usuário envia um arquivo (POST).

3) UploadForm valida se o arquivo foi enviado e se o tipo é permitido.

4) O nome do arquivo é normalizado (secure_filename) e salvo na pasta UPLOAD_FOLDER.

5) Usuário é redirecionado para /arquivo/<nome>, que exibe o arquivo no navegador.

6) Caso inválido, é exibida mensagem de erro (flash).

```python
from flask import send_from_directory

# Rota para upload de arquivos
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()  # Instancia o formulário definido em forms.py

    # Verifica se o formulário foi enviado (POST) e se passou na validação
    if form.validate_on_submit():
        f = form.arquivo.data  # Objeto FileStorage do arquivo enviado

        # Confere se existe arquivo e se a extensão é permitida
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)  # Normaliza o nome do arquivo

            # Opcional: prefixo temporal para evitar colisões de nomes
            import time
            filename = f"{int(time.time())}_{filename}"

            # Salva o arquivo na pasta configurada
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Mensagem de sucesso exibida no layout.html
            flash('Arquivo enviado com sucesso!', 'success')

            # Redireciona para a rota que exibe o arquivo
            return redirect(url_for('mostrar_arquivo', filename=filename))

        # Caso a extensão não seja válida
        flash('Tipo de arquivo não permitido', 'error')

    # Se for GET (primeiro acesso) ou se houver erros, renderiza o formulário de upload
    return render_template('upload.html', form=form)


# Rota para exibir ou baixar o arquivo enviado
@app.route('/arquivo/<path:filename>')
def mostrar_arquivo(filename):
    # Busca o arquivo salvo na pasta UPLOAD_FOLDER
    # as_attachment=False → abre no navegador (se for imagem/pdf), ao invés de forçar download
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

```

Template (`templates/upload.html`) — **atenção ao `enctype`**:


```html
{# Herda a estrutura base de layout.html (HTML principal + mensagens flash) #}
{% extends "layout.html" %}

{# Importa o macro render_field definido em macros.html,
   que ajuda a renderizar campos de formulário com label + input + erros #}
{% from "macros.html" import render_field %}

{% block content %}
  <h1>Envio de Arquivos</h1>

  {# Formulário com enctype="multipart/form-data",
     obrigatório para permitir upload de arquivos #}
  <form method="POST" enctype="multipart/form-data">
    
    {# Token CSRF (segurança contra ataques Cross-Site Request Forgery) #}
    {{ form.csrf_token }}

    {# Campo de seleção de arquivo renderizado via macro (FileField do Flask-WTF) #}
    {{ render_field(form.arquivo) }}

    {# Botão de envio do formulário #}
    <button type="submit">Enviar</button>
  </form>
{% endblock %}

```

Pontos importantes:

enctype="multipart/form-data" é obrigatório para que arquivos sejam enviados corretamente.

form.csrf_token é gerado pelo Flask-WTF para validar o formulário e proteger contra CSRF.

O render_field vem do macro em macros.html, que já inclui label, input e mensagens de erro.

O botão dispara o envio (POST) para a mesma rota (/upload).


