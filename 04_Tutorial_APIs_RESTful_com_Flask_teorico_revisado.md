# Tutorial de APIs RESTful com Flask  
## (Conceitos, Teoria e Implementação Prática)

Este guia foi elaborado para quem **nunca trabalhou com APIs**. Antes de programar, vamos entender **o que é uma API RESTful, para que serve, e por que ela é tão importante**. Depois, construiremos uma aplicação completa com Flask.

---

## 0. O que será feito e por que?

O objetivo é **criar uma API RESTful** usando Flask. Isso significa que construiremos uma interface que outros programas poderão usar para **enviar e receber dados estruturados** em **JSON**.

Por que isso é importante?
- Aplicações modernas (web, mobile, IoT) precisam se comunicar entre si.  
- Uma API bem projetada permite que **aplicações diferentes conversem**, independentemente da linguagem usada.  
- É a base para **sistemas distribuídos**, **microserviços** e **integrações entre empresas**.  

---

## 1. Conceitos Fundamentais

### O que é uma API?
API significa **Application Programming Interface** (Interface de Programação de Aplicações).  
Ela define **como diferentes sistemas podem se comunicar** de forma padronizada.

### O que é REST?
REST (**Representational State Transfer**) é um **estilo de arquitetura** que usa o protocolo HTTP para criar APIs de forma simples, escalável e independente.  
As principais características são:
- **Recursos representados como URLs** (ex.: `/usuarios/1`).  
- **Métodos HTTP bem definidos** para operações:  
  - **GET** → buscar dados.  
  - **POST** → criar novo recurso.  
  - **PUT/PATCH** → atualizar recurso existente.  
  - **DELETE** → excluir recurso.  
- **Formato de dados padronizado** (geralmente JSON).  

### Por que JSON?
JSON (JavaScript Object Notation) é leve, fácil de ler e amplamente suportado. É o formato padrão para troca de dados em APIs.

---

## 2. Estrutura do Projeto

```
/meu_projeto
|-- app.py
|-- requirements.txt
```

---

## 3. Criando uma API RESTful no Flask

### Arquivo `app.py`

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# Simulação de "banco de dados" em memória
usuarios = [
    {"id": 1, "nome": "Alice", "email": "alice@example.com"},
    {"id": 2, "nome": "Bob", "email": "bob@example.com"}
]

@app.route('/')
def home():
    return "<h1>API RESTful com Flask</h1><p>Use os endpoints /api/usuarios</p>"
```

---

## 4. Implementando os Endpoints CRUD

### 4.1 Listar Todos os Usuários (GET)
```python
@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    return jsonify(usuarios)
```

### 4.2 Obter Usuário por ID (GET)
```python
@app.route('/api/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    usuario = next((u for u in usuarios if u["id"] == id), None)
    if usuario:
        return jsonify(usuario)
    return jsonify({"erro": "Usuário não encontrado"}), 404
```

### 4.3 Criar Novo Usuário (POST)
```python
@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json()
    novo = {
        "id": len(usuarios) + 1,
        "nome": dados.get("nome"),
        "email": dados.get("email")
    }
    usuarios.append(novo)
    return jsonify(novo), 201
```

### 4.4 Atualizar Usuário (PUT)
```python
@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    usuario = next((u for u in usuarios if u["id"] == id), None)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    dados = request.get_json()
    usuario["nome"] = dados.get("nome", usuario["nome"])
    usuario["email"] = dados.get("email", usuario["email"])
    return jsonify(usuario)
```

### 4.5 Excluir Usuário (DELETE)
```python
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    global usuarios
    usuarios = [u for u in usuarios if u["id"] != id]
    return jsonify({"mensagem": f"Usuário {id} excluído com sucesso"})
```

---

## 5. Testando a API

### Executando
```bash
python app.py
```
Acesse em:  
👉 `http://127.0.0.1:5000/`

### Ferramentas para testar
- **cURL** (linha de comando).  
- **Postman** (interface gráfica).  
- **Insomnia** (focado em APIs).  

Exemplo com cURL:
```bash
curl http://127.0.0.1:5000/api/usuarios
```

Criando usuário:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"nome":"Carlos","email":"carlos@example.com"}' http://127.0.0.1:5000/api/usuarios
```

---

## 6. Boas Práticas e Próximos Passos

- Sempre retornar **JSON padronizado**.  
- Usar **códigos HTTP corretos** (`200`, `201`, `404`).  
- Validar dados de entrada antes de salvar.  
- Em projetos maiores, considerar:
  - **Flask-RESTful** → adiciona abstrações úteis para criar APIs.  
  - **Flask-RESTx** → suporte a documentação automática (Swagger/OpenAPI).  
  - **Autenticação e Autorização** (com Flask-Login ou JWT).  
  - **Banco de Dados real** (com SQLAlchemy ou outro ORM).  

---

✅ Agora você entende **o que é uma API RESTful, por que ela é importante e como criar uma API completa com Flask**, pronta para ser consumida por outros sistemas.
