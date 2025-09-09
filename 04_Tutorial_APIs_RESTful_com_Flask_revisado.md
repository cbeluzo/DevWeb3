# Tutorial de APIs RESTful com Flask

Este guia mostra como construir **APIs RESTful** usando Flask, permitindo que sua aplicação se comunique com outros serviços e clientes externos (como aplicações web, mobile ou outros sistemas).

---

## 1. O que é uma API RESTful?

Uma **API RESTful** segue os princípios da arquitetura REST (Representational State Transfer).  
Ela utiliza os métodos HTTP para definir as operações possíveis:

- **GET** → buscar informações.  
- **POST** → criar um novo recurso.  
- **PUT/PATCH** → atualizar um recurso existente.  
- **DELETE** → remover um recurso.  

O resultado é geralmente retornado em **formato JSON**, que é amplamente utilizado por sistemas distribuídos.

---

## 2. Estrutura do Projeto

```
/meu_projeto
|-- app.py
|-- /templates
|   |-- index.html
|-- requirements.txt
```

---

## 3. Configuração Inicial (`app.py`)

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# Exemplo de "banco de dados" em memória
usuarios = [
    {"id": 1, "nome": "Alice", "email": "alice@example.com"},
    {"id": 2, "nome": "Bob", "email": "bob@example.com"}
]

@app.route('/')
def home():
    return "<h1>API RESTful com Flask</h1><p>Use os endpoints /api/usuarios</p>"
```

---

## 4. Criando Endpoints RESTful

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

1. Rode a aplicação:
   ```bash
   python app.py
   ```
   Acesse `http://127.0.0.1:5000/`.

2. Teste os endpoints usando ferramentas como:
   - **cURL** (linha de comando)  
   - **Postman**  
   - **Insomnia**  

Exemplos com `curl`:

- Listar usuários:
  ```bash
  curl http://127.0.0.1:5000/api/usuarios
  ```

- Criar usuário:
  ```bash
  curl -X POST -H "Content-Type: application/json"   -d '{"nome":"Carlos","email":"carlos@example.com"}'   http://127.0.0.1:5000/api/usuarios
  ```

---

## 6. Boas Práticas

- Sempre retornar **JSON estruturado**.  
- Usar **códigos HTTP adequados** (`200 OK`, `201 Created`, `404 Not Found`, etc.).  
- Validar os dados recebidos (`request.get_json()`).  
- Considerar o uso de **Flask-RESTful** ou **Flask-RESTx** em projetos maiores, para facilitar organização.  

---

✅ Agora você tem uma **API RESTful funcional** no Flask, com operações CRUD completas.
