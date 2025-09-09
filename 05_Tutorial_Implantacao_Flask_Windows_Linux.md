# Tutorial de Implantação de Aplicações Flask  
## (Conceitos, Gunicorn/Waitress, Nginx, HTTPS e Free Tier)

Este guia mostra como colocar sua aplicação Flask em produção tanto em **Linux** quanto em **Windows**.  
Antes de iniciar, revisamos **o que será feito** e **por que** cada tecnologia é necessária. Depois, seguimos com passos práticos para cada sistema operacional.

---

## 0. O que será feito e por que?

Nosso objetivo é levar uma aplicação Flask para **produção**, ou seja, torná-la acessível fora do ambiente local de desenvolvimento.  
- Em **Linux**, usaremos a combinação consolidada **Nginx + Gunicorn + systemd + Certbot (HTTPS)**.  
- Em **Windows**, o Gunicorn não funciona bem, então usaremos o **Waitress** (servidor WSGI puro-Python) ou integração com IIS/WFastCGI para Windows Server.  

Ao final, também mostraremos como fazer deploy em **free tiers** (Render, Railway, Heroku), que abstraem toda a infraestrutura.  

---

## 1. Conceitos Fundamentais

- **Flask** → framework web em Python.  
- **WSGI** → padrão que define como aplicações Python conversam com servidores web.  
- **Gunicorn** → servidor WSGI popular em produção, mas limitado a Unix/Linux.  
- **Waitress** → alternativa compatível com Windows, puro-Python.  
- **Nginx** → servidor web usado como **proxy reverso** para receber conexões HTTP/HTTPS e encaminhar ao servidor WSGI.  
- **systemd** → gerenciador de processos em Linux. Garante reinício automático e logs.  
- **Certbot/Let’s Encrypt** → fornece certificados HTTPS gratuitos.  
- **Free tier (Render, Railway, Heroku)** → serviços em nuvem que cuidam do servidor web, HTTPS e escala automaticamente.  

---

## 2. Estrutura de Projeto

```
/meu_projeto
|-- app.py
|-- wsgi.py
|-- requirements.txt
```

**`app.py`** (mínimo funcional):
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Aplicação Flask em produção."
```

**`wsgi.py`**:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

**`requirements.txt`**:
```
Flask>=3.0
gunicorn>=21.0   # Linux
waitress>=3.0    # Windows
```

---

# Parte A – Implantação em Linux (Nginx + Gunicorn)

### 1. Executando com Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

### 2. Mantendo o serviço com systemd

Arquivo `/etc/systemd/system/flaskapp.service`:
```
[Unit]
Description=Gunicorn para Flask (produção)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/meu_projeto
ExecStart=/caminho/para/venv/bin/gunicorn --workers 3 --bind unix:flaskapp.sock wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp
```

### 3. Configurando o Nginx

Arquivo `/etc/nginx/sites-available/flaskapp`:
```
server {
    listen 80;
    server_name exemplo.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/caminho/para/meu_projeto/flaskapp.sock;
    }
}
```

Ativar:
```bash
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled
sudo systemctl reload nginx
```

### 4. HTTPS com Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d exemplo.com -d www.exemplo.com
```

---

# Parte B – Implantação em Windows (Waitress)

### 1. Gunicorn não funciona no Windows

Por limitações internas, o **Gunicorn não roda bem em Windows**.  
A alternativa recomendada é usar o **Waitress**.

### 2. Executando com Waitress

Instale:
```bash
pip install waitress
```

Execute:
```bash
waitress-serve --listen=0.0.0.0:8000 wsgi:app
```

Agora sua aplicação Flask está acessível na porta 8000.

### 3. Opções adicionais em Windows Server

- **IIS + WFastCGI** → integração oficial do Flask/Django em Windows Server.  
- **Docker Desktop** → crie containers Linux no Windows e rode o mesmo stack Linux (Nginx + Gunicorn).  

---

# Parte C – Deploy em Free Tier (Render, Railway e Heroku)

Nem sempre precisamos configurar servidores manualmente (Linux/Windows). Para protótipos, ensino ou MVPs, os **serviços em nuvem com free tier** são a forma mais rápida de publicar uma aplicação Flask.  

Essas plataformas cuidam automaticamente de:
- **Servidor web (Nginx ou equivalente)**.  
- **Servidor WSGI (Gunicorn ou outro)**.  
- **Escalabilidade mínima** (processos múltiplos).  
- **HTTPS gratuito com Let’s Encrypt**.  
- **Logs acessíveis via painel**.  

Você só precisa fornecer:
1. O código da aplicação (via GitHub ou upload).  
2. Um **arquivo `requirements.txt`** com dependências.  
3. Um **Procfile** (arquivo de texto que indica o comando de inicialização).  

---

## C.1 Deploy no Render

### O que é o Render?
- Plataforma moderna de hospedagem de aplicações web, com **free tier** suficiente para protótipos.  
- Permite deploy contínuo integrado ao **GitHub**.  
- Inclui HTTPS automático, logs e variáveis de ambiente.

### Passo a Passo
1. Crie uma conta gratuita em [https://render.com](https://render.com).  
2. Conecte sua conta ao GitHub.  
3. Clique em **New + → Web Service**.  
4. Selecione o repositório que contém sua aplicação Flask.  
5. Defina:
   - **Build Command**:  
     ```
     pip install -r requirements.txt
     ```
   - **Start Command** (em Procfile ou campo direto):  
     ```
     gunicorn wsgi:app
     ```
6. O Render fará o build e disponibilizará uma URL pública como:  
   ```
   https://meu-app.onrender.com
   ```
7. (Opcional) Configure variáveis de ambiente no painel em **Environment** (ex.: `SECRET_KEY`, configs de banco).

### Limites do Free Tier
- Recursos de CPU e RAM limitados.  
- Aplicação pode hibernar após períodos de inatividade.  
- Recomendado para **testes e ensino**, não para produção pesada.

---

## C.2 Deploy no Railway

### O que é o Railway?
- Plataforma similar ao Render, também com free tier.  
- Suporta deploy a partir do GitHub ou upload manual.  
- Gera automaticamente HTTPS.  

### Passo a Passo
1. Crie conta em [https://railway.app](https://railway.app).  
2. Clique em **New Project**.  
3. Conecte ao GitHub e selecione seu repositório Flask.  
4. Railway detecta automaticamente `requirements.txt` e instala dependências.  
5. Crie um **Procfile** (caso queira customizar):
   ```
   web: gunicorn wsgi:app
   ```
6. Após o build, Railway disponibiliza URL pública como:  
   ```
   https://meu-app.up.railway.app
   ```
7. Configure variáveis de ambiente em **Settings → Variables**.

### Limites do Free Tier
- Créditos mensais (geralmente ~5 USD em uso).  
- Projeto pode pausar ao atingir limite.  
- Ideal para projetos pequenos e demonstrações.

---

## C.3 Deploy no Heroku (quando disponível)

### O que é o Heroku?
- Uma das primeiras plataformas de **PaaS (Platform as a Service)**.  
- Ficou famosa pela simplicidade de deploy via Git.  
- Atualmente, o free tier é mais restrito, mas ainda usado em contextos acadêmicos.

### Passo a Passo
1. Instale a **CLI do Heroku**:  
   [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)  
2. Faça login:  
   ```bash
   heroku login
   ```
3. Crie um novo app:  
   ```bash
   heroku create meu-app
   ```
4. Prepare os arquivos obrigatórios:  
   - **requirements.txt**  
   - **Procfile**:
     ```
     web: gunicorn wsgi:app
     ```
     (No Windows, pode usar Waitress)  
     ```
     web: waitress-serve --listen=0.0.0.0:$PORT wsgi:app
     ```
5. Faça push do código:  
   ```bash
   git push heroku main
   ```
6. Acesse:  
   ```
   https://meu-app.herokuapp.com
   ```

### Limites do Free Tier
- Aplicações hibernam após inatividade.  
- Limite de horas/mês de execução.  
- Não recomendado para produção séria, mas ótimo para ensino e protótipos.

---

## Comparação Rápida

| Plataforma | Deploy via GitHub | HTTPS automático | Limites Free Tier | Recomendado para |
|------------|------------------|------------------|-------------------|------------------|
| **Render** | Sim              | Sim              | Hiberna após inatividade | Ensino, protótipos |
| **Railway**| Sim              | Sim              | Créditos mensais (~5 USD) | Testes, MVPs |
| **Heroku** | Sim (via Git)    | Sim              | Horas/mês limitadas | Ensino, aprendizado |

---


---

## Resumo Final

- **Linux (produção clássica)**: Nginx + Gunicorn + systemd + Certbot.  
- **Windows (desenvolvimento/testes)**: Waitress (`waitress-serve`).  
- **Windows Server (produção)**: IIS + WFastCGI ou Docker Desktop.  
- **Free tier**: Render, Railway, Heroku → mais simples, com HTTPS automático.  

