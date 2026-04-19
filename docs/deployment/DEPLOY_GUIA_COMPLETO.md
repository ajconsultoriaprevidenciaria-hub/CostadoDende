# 🚀 GUIA DE DEPLOY - COSTA DO DENDÊ - HOSTINGER

Deploy passo a passo via SSH para Hostinger.  
**Tempo estimado:** 20-30 minutos

---

## 📋 PRÉ-REQUISITOS

Antes de começar, tenha em mãos:

- ✅ Acesso SSH (IP: 82.180.153.36, Porta: 65002, User: u978535582)
- ✅ Domínio configurado (postoscostadodende.com.br)
- ✅ Painel Hostinger aberto

---

## 🎯 PASSO 1: CONECTAR VIA SSH

No seu terminal local, execute:

```bash
ssh -p 65002 u978535582@82.180.153.36
```

Digite a senha quando solicitado.

**✋ PARE AQUI - Confirme que conectou antes de continuar!**

---

## 📦 PASSO 2: VERIFICAR AMBIENTE

No servidor (via SSH), execute estes comandos para ver o que está disponível:

```bash
# Ver versão do Python
python --version
python3 --version

# Ver MySQL disponível
mysql --version

# Ver estrutura de pastas
pwd
ls -la
```

**📸 Me envie a saída desses comandos para eu confirmar o ambiente!**

---

## 🗄️ PASSO 3: CRIAR BANCO DE DADOS VIA PAINEL

**Vá ao painel Hostinger** (não via SSH):

1. **hPanel** → **Bancos de Dados** → **Gerenciar**
2. Clique em **Criar Novo Banco de Dados**
3. Preencha:
   - **Nome do banco:** `u978535582_costadodende`
   - **Nome de usuário:** `u978535582_costadodende` (ou use existente)
   - **Senha:** Anote! (Você vai usar depois)
4. Clique em **Criar**

**✋ Criou o banco? Anote as credenciais:**

- Nome do banco: `_________________`
- Usuário: `_________________`
- Senha: `_________________`
- Host: `localhost` (padrão)

---

## 📂 PASSO 4: PREPARAR DIRETÓRIO NO SERVIDOR

De volta ao terminal SSH:

```bash
# Ver onde estamos
pwd

# Criar estrutura (se não existir)
mkdir -p public_html
cd public_html

# Limpar se necessário (CUIDADO!)
# ls -la
```

**💡 Qual pasta você está? Me envie o resultado de `pwd`**

---

## 📤 PASSO 5: FAZER UPLOAD DOS ARQUIVOS

Você tem 3 opções:

### **Opção A: Via SCP (do seu computador local)** ⭐ Recomendado

No seu terminal **LOCAL** (não SSH), execute:

```bash
cd /home/davidsonc/development/CostadoDende

# Criar pacote limpo
tar --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='*.sqlite3' \
    --exclude='venv' \
    --exclude='env' \
    --exclude='staticfiles/*' \
    --exclude='media/*' \
    -czf costadodende_deploy.tar.gz \
    apps/ config/ templates/ static/ \
    manage.py passenger_wsgi.py requirements.txt \
    .env.production.example

# Enviar para o servidor
scp -P 65002 costadodende_deploy.tar.gz u978535582@82.180.153.36:~/public_html/

# Conectar novamente via SSH
ssh -p 65002 u978535582@82.180.153.36
```

No servidor SSH, extrair:

```bash
cd ~/public_html
tar -xzf costadodende_deploy.tar.gz
rm costadodende_deploy.tar.gz
ls -la
```

### **Opção B: Via Git Clone**

No servidor SSH:

```bash
cd ~/public_html
git clone https://github.com/ajconsultoriaprevidenciaria-hub/CostadoDende.git .
```

### **Opção C: Via Painel (Upload ZIP)**

1. No painel Hostinger → Gerenciador de Arquivos
2. Faça upload do ZIP
3. Extraia lá

**✋ Qual opção você usou? Confirme que os arquivos estão lá com `ls -la`**

---

## 🔧 PASSO 6: CRIAR ARQUIVO .env

No servidor SSH:

```bash
cd ~/public_html

# Gerar SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

**📋 Copie o resultado (sua SECRET_KEY)**

Agora crie o arquivo `.env`:

```bash
nano .env
```

Cole este conteúdo (AJUSTE OS VALORES!):

```env
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY=COLE_A_SECRET_KEY_GERADA_ACIMA
DEBUG=False

DJANGO_ALLOWED_HOSTS=postoscostadodende.com.br,www.postoscostadodende.com.br

DB_ENGINE=django.db.backends.mysql
DB_NAME=u978535582_costadodende
DB_USER=u978535582_costadodende
DB_PASSWORD=SENHA_DO_BANCO_CRIADO_NO_PASSO_3
DB_HOST=localhost
DB_PORT=3306

DJANGO_CSRF_TRUSTED_ORIGINS=https://postoscostadodende.com.br,https://www.postoscostadodende.com.br
```

Salvar: `Ctrl+O` → Enter → `Ctrl+X`

**✋ Criou o .env? Verificar: `cat .env`**

---

## 🐍 PASSO 7: CONFIGURAR PYTHON APP (PAINEL)

**Vá ao painel Hostinger:**

1. **hPanel** → **Avançado** → **Aplicativo Python**
2. Clique em **Criar Aplicação**
3. Preencha:
   - **Versão Python:** 3.11 ou 3.12
   - **Diretório raiz:** `public_html`
   - **URL:** `postoscostadodende.com.br`
   - **Arquivo de inicialização:** `passenger_wsgi.py`
4. Clique em **Criar**

**✋ Anotou o caminho do virtualenv?** Exemplo:  
`/home/u978535582/virtualenv/public_html/3.11`

---

## 📦 PASSO 8: INSTALAR DEPENDÊNCIAS

No servidor SSH:

```bash
# Ativar virtualenv (ajuste a versão do Python)
source ~/virtualenv/public_html/3.11/bin/activate

# Verificar Python no virtualenv
which python
python --version

# Instalar dependências
cd ~/public_html
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalação
pip list
```

**✋ Algum erro? Me envie a mensagem completa!**

---

## 🗃️ PASSO 9: RODAR MIGRATIONS

No servidor SSH (com virtualenv ativado):

```bash
cd ~/public_html

# Testar configuração
python manage.py check

# Rodar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

**✋ Criou o superusuário? Anote usuário/senha!**

---

## 🔄 PASSO 10: REINICIAR APLICAÇÃO

**Opção A: Via Painel**

- hPanel → Aplicativo Python → Reiniciar

**Opção B: Via SSH**

```bash
mkdir -p tmp
touch tmp/restart.txt
```

---

## 🌐 PASSO 11: CONFIGURAR SSL/HTTPS

**No painel Hostinger:**

1. **hPanel** → **SSL**
2. Ativar **SSL Gratuito (Let's Encrypt)**
3. Aguardar 5-10 minutos

---

## ✅ PASSO 12: TESTAR O SITE

Abra no navegador:

- https://postoscostadodende.com.br
- https://postoscostadodende.com.br/admin

**Login com o superusuário criado!**

---

## 🔧 COMANDOS ÚTEIS

```bash
# Ver logs de erro
tail -f ~/logs/error.log

# Reiniciar app
touch ~/public_html/tmp/restart.txt

# Acessar banco de dados
mysql -u u978535582_costadodende -p u978535582_costadodende

# Ver processos Python
ps aux | grep python

# Ver variáveis de ambiente
cat .env
```

---

## 🆘 PROBLEMAS COMUNS

### **500 Internal Server Error**

```bash
# Verificar logs
tail -50 ~/logs/error.log

# Verificar permissões
chmod 755 ~/public_html
chmod 644 ~/public_html/.env
```

### **Banco não conecta**

```bash
# Testar conexão MySQL
mysql -u u978535582_costadodende -p -h localhost

# Verificar .env
cat .env | grep DB_
```

### **Arquivos estáticos não carregam**

```bash
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

---

## 📞 SUPORTE

Me chame com:

- Mensagem de erro completa
- Resultado de `tail -50 ~/logs/error.log`
- Resultado de `ls -la ~/public_html`

---

**🎉 BOA SORTE!**
