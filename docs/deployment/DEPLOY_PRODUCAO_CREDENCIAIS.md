# 🔒 Documentação de Deploy - Costa do Dendê - PRODUÇÃO

**⚠️ ARQUIVO CONFIDENCIAL - NÃO COMMITAR NO GIT ⚠️**

Data de Deploy: 18 de Abril de 2026  
Responsável: Davidson Campos  
Sistema: Costa do Dendê - Gestão de Frotas e Postos

---

## 📡 SERVIDOR VPS - HOSTINGER

### Informações do Servidor

- **Provedor:** Hostinger
- **Plano:** KVM 2
- **IP Público:** `72.61.27.65`
- **Sistema Operacional:** Ubuntu 24.04.4 LTS (Noble Numbat)
- **Kernel:** 6.8.0-110-generic (após reboot)
- **Arquitetura:** x86_64
- **Recursos:**
  - RAM: 8GB
  - vCPU: 2 cores
  - Storage: 100GB NVMe SSD
  - Largura de Banda: Ilimitada
  - Datacenter: Brasil

### Acesso SSH

```bash
ssh root@72.61.27.65
```

- **Usuário:** `root`
- **Senha:** `Vps6558costadodendE@`
- **Porta SSH:** 22 (padrão)

### Usuário do Sistema (Aplicação)

- **Usuário:** `costadodende`
- **Home Directory:** `/home/costadodende`
- **Shell:** `/bin/bash`
- **Sem senha** (acesso apenas via root/sudo)

---

## 🗄️ BANCO DE DADOS - POSTGRESQL

### Instalação

- **Versão:** PostgreSQL 16.13
- **Pacotes:** `postgresql postgresql-contrib libpq-dev`

### Configuração do Banco

- **Nome do Banco:** `costadodende_db`
- **Usuário:** `costadodende_user`
- **Senha:** `CostaDende2026`
- **Host:** `localhost`
- **Porta:** `5432`
- **Encoding:** UTF8
- **Locale:** C.UTF-8
- **Timezone:** Etc/UTC

### Comandos de Criação

```sql
CREATE DATABASE costadodende_db;
CREATE USER costadodende_user WITH PASSWORD 'CostaDende2026';
GRANT ALL PRIVILEGES ON DATABASE costadodende_db TO costadodende_user;
GRANT ALL ON SCHEMA public TO costadodende_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO costadodende_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO costadodende_user;
```

### Acesso ao Banco

```bash
# Como usuário postgres
sudo -u postgres psql

# Conectar ao banco específico
sudo -u postgres psql -d costadodende_db

# Como usuário da aplicação (requer configuração pg_hba.conf)
psql -h localhost -U costadodende_user -d costadodende_db
```

---

## 🐍 PYTHON E AMBIENTE VIRTUAL

### Python

- **Versão:** Python 3.12.3
- **Pip:** 26.0.1
- **Localização:** `/usr/bin/python3`

### Virtualenv

- **Localização:** `/home/costadodende/venv`
- **Comando de Criação:** `python3 -m venv /home/costadodende/venv`
- **Ativação:** `source /home/costadodende/venv/bin/activate`

### Dependências Python Instaladas

```txt
django==6.0.4
plotly==6.7.0
reportlab==4.4.10
pandas==3.0.2
Pillow==12.2.0
whitenoise==6.12.0
gunicorn==23.0.0
psycopg2-binary==2.9.11
python-dotenv==1.2.2
asgiref==3.11.1
sqlparse==0.5.5
numpy==2.4.4
narwhals==2.19.0
charset-normalizer==3.4.7
```

**IMPORTANTE:** MySQL/mysqlclient foi REMOVIDO do projeto. Sistema usa apenas PostgreSQL.

---

## 🚀 APLICAÇÃO DJANGO

### Estrutura de Diretórios

```
/home/costadodende/
├── app/                          # Aplicação Django
│   ├── apps/                     # Apps Django
│   │   ├── core/
│   │   ├── fretes/
│   │   ├── dashboard/
│   │   └── motorista_portal/
│   ├── config/                   # Configurações
│   │   ├── settings.py
│   │   ├── settings_production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── templates/                # Templates HTML
│   ├── static/                   # Arquivos estáticos fonte
│   ├── staticfiles/              # Arquivos estáticos coletados
│   ├── media/                    # Uploads de usuários
│   ├── manage.py
│   ├── passenger_wsgi.py
│   ├── requirements.txt
│   └── .env                      # Variáveis de ambiente
├── venv/                         # Ambiente virtual Python
├── costadodende_deploy.tar.gz    # Pacote de deploy
└── [logs]
```

### Arquivo .env (Produção)

**Localização:** `/home/costadodende/app/.env`

```env
DEBUG=False
DJANGO_SECRET_KEY=c0st4d0d3nd3-pr0duct10n-s3cr3t-k3y-1776520692-49e550f11e93b61580d97cf5b39adffe
DJANGO_ALLOWED_HOSTS=postoscostadodende.com.br,www.postoscostadodende.com.br,72.61.27.65,localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=costadodende_db
DB_USER=costadodende_user
DB_PASSWORD=CostaDende2026
DB_HOST=localhost
DB_PORT=5432
TIMEZONE=America/Bahia
```

### Superusuário Django (Admin)

- **Usuário:** `admin`
- **Senha:** `Admin@Costa2026`
- **Email:** `admin@postoscostadodende.com.br`
- **URL Admin:** `http://72.61.27.65/admin` (temporário até DNS)

### Comandos Django Executados

```bash
# Migrations
/home/costadodende/venv/bin/python manage.py migrate --settings=config.settings_production

# Coletar arquivos estáticos
/home/costadodende/venv/bin/python manage.py collectstatic --noinput --settings=config.settings_production

# Criar superusuário (via shell)
/home/costadodende/venv/bin/python manage.py shell --settings=config.settings_production
```

---

## 🦄 GUNICORN (WSGI SERVER)

### Configuração

- **Versão:** 23.0.0
- **Workers:** 3
- **Bind:** `127.0.0.1:8000`
- **Timeout:** 60 segundos
- **Usuário:** `costadodende`
- **Settings Module:** `config.settings_production`

### Logs

- **Access Log:** `/var/log/costadodende/access.log`
- **Error Log:** `/var/log/costadodende/error.log`
- **Proprietário:** `costadodende:costadodende`

### Comando de Execução

```bash
/home/costadodende/venv/bin/gunicorn config.wsgi:application \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /var/log/costadodende/access.log \
    --error-logfile /var/log/costadodende/error.log \
    --env DJANGO_SETTINGS_MODULE=config.settings_production
```

---

## 👁️ SUPERVISOR (GERENCIADOR DE PROCESSOS)

### Instalação

- **Versão:** 4.2.5
- **Service:** `supervisor.service`

### Arquivo de Configuração

**Localização:** `/etc/supervisor/conf.d/costadodende.conf`

```ini
[program:costadodende]
directory=/home/costadodende/app
command=/home/costadodende/venv/bin/gunicorn config.wsgi:application \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /var/log/costadodende/access.log \
    --error-logfile /var/log/costadodende/error.log \
    --env DJANGO_SETTINGS_MODULE=config.settings_production
user=costadodende
autostart=true
autorestart=true
redirect_stderr=true
stopasgroup=true
killasgroup=true
```

### Comandos Supervisor

```bash
# Recarregar configuração
supervisorctl reread
supervisorctl update

# Controlar aplicação
supervisorctl start costadodende
supervisorctl stop costadodende
supervisorctl restart costadodende
supervisorctl status costadodende

# Ver logs em tempo real
supervisorctl tail -f costadodende stdout
supervisorctl tail -f costadodende stderr
```

---

## 🌐 NGINX (SERVIDOR WEB)

### Instalação

- **Versão:** 1.24.0 (Ubuntu)
- **Service:** `nginx.service`

### Arquivo de Configuração

**Localização:** `/etc/nginx/sites-available/costadodende`  
**Link Simbólico:** `/etc/nginx/sites-enabled/costadodende`

```nginx
server {
    listen 80;
    server_name postoscostadodende.com.br www.postoscostadodende.com.br 72.61.27.65;
    client_max_body_size 20M;

    access_log /var/log/nginx/costadodende_access.log;
    error_log /var/log/nginx/costadodende_error.log;

    location /static/ {
        alias /home/costadodende/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/costadodende/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

### Comandos Nginx

```bash
# Testar configuração
nginx -t

# Recarregar (sem downtime)
systemctl reload nginx

# Reiniciar (com breve downtime)
systemctl restart nginx

# Status
systemctl status nginx

# Logs
tail -f /var/log/nginx/costadodende_access.log
tail -f /var/log/nginx/costadodende_error.log
```

### Site Padrão

- **Removido:** `/etc/nginx/sites-enabled/default` (foi deletado)

---

## 🔐 SSL/TLS - LET'S ENCRYPT (CERTBOT)

### Instalação

- **Versão:** 2.9.0
- **Plugin:** `python3-certbot-nginx`

### Status Atual

❌ **SSL NÃO CONFIGURADO** - Aguardando configuração DNS

### Pré-requisitos para SSL

O domínio `postoscostadodende.com.br` deve apontar para o IP `72.61.27.65`:

**Registros DNS necessários:**

```
Tipo: A
Nome: @
Valor: 72.61.27.65
TTL: 3600

Tipo: CNAME
Nome: www
Valor: postoscostadodende.com.br
TTL: 3600
```

### Comando para Obter Certificado (após DNS configurado)

```bash
certbot --nginx \
    -d postoscostadodende.com.br \
    -d www.postoscostadodende.com.br \
    --non-interactive \
    --agree-tos \
    --email admin@postoscostadodende.com.br \
    --redirect
```

### Renovação Automática

- **Timer:** `certbot.timer`
- **Comando:** `systemctl status certbot.timer`
- **Teste:** `certbot renew --dry-run`

---

## 🔥 FIREWALL - UFW

### Status

✅ **ATIVO** - Firewall habilitado e rodando

### Regras Configuradas

```bash
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere    # SSH
80/tcp                     ALLOW       Anywhere    # HTTP
443/tcp                    ALLOW       Anywhere    # HTTPS
22/tcp (v6)                ALLOW       Anywhere (v6)
80/tcp (v6)                ALLOW       Anywhere (v6)
443/tcp (v6)               ALLOW       Anywhere (v6)
```

### Comandos UFW

```bash
# Status
ufw status verbose

# Adicionar regra
ufw allow 22/tcp

# Remover regra
ufw delete allow 22/tcp

# Desabilitar (CUIDADO!)
ufw disable

# Habilitar
ufw enable
```

---

## 🌍 DOMÍNIO E DNS

### Domínio

- **Domínio Principal:** `postoscostadodende.com.br`
- **Subdomínio WWW:** `www.postoscostadodende.com.br`

### Status DNS

⚠️ **PENDENTE** - DNS ainda não foi configurado para apontar para o VPS

### Configuração Necessária

Acessar o painel de gerenciamento do domínio (Registro.br ou provedor DNS) e adicionar:

```
# Registro A (domínio principal)
Tipo: A
Host: @
Endereço IPv4: 72.61.27.65
TTL: 3600

# Registro CNAME (www)
Tipo: CNAME
Host: www
Aponta para: postoscostadodende.com.br
TTL: 3600
```

### URLs de Acesso

**Atual (via IP):**

- Aplicação: `http://72.61.27.65`
- Login: `http://72.61.27.65/login/`
- Admin: `http://72.61.27.65/admin`

**Futuro (após DNS + SSL):**

- Aplicação: `https://postoscostadodende.com.br`
- Login: `https://postoscostadodende.com.br/login/`
- Admin: `https://postoscostadodende.com.br/admin`

---

## 📦 PACOTES DO SISTEMA INSTALADOS

### Pacotes APT

```bash
# Banco de dados
postgresql
postgresql-contrib
libpq-dev

# Servidor web
nginx

# Python e desenvolvimento
python3-pip
python3-venv
python3-dev
python3.12-dev
libpython3.12-dev

# Compilação
build-essential
gcc-13
g++-13
make

# SSL
certbot
python3-certbot-nginx

# Gerenciamento de processos
supervisor

# Utilitários
curl
wget
git (provavelmente já instalado)
```

### Versões dos Principais Serviços

- Ubuntu: 24.04.4 LTS
- PostgreSQL: 16.13
- Nginx: 1.24.0
- Python: 3.12.3
- Pip: 26.0.1
- Gunicorn: 23.0.0
- Supervisor: 4.2.5
- Certbot: 2.9.0
- Django: 6.0.4

---

## 🔄 PROCESSO DE DEPLOY

### 1. Preparação Local

```bash
# Remover mysqlclient do requirements.txt
# Adicionar python-dotenv ao requirements.txt
# Modificar manage.py para carregar .env
# Modificar settings_production.py para carregar .env

# Criar pacote de deploy
tar --exclude='*.pyc' --exclude='__pycache__' \
    -czf costadodende_deploy.tar.gz \
    -C /home/davidsonc/development/CostadoDende \
    apps config templates static manage.py passenger_wsgi.py requirements.txt
```

### 2. Setup do Servidor

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências
apt install -y postgresql postgresql-contrib nginx \
    python3-pip python3-venv python3-dev libpq-dev \
    build-essential certbot python3-certbot-nginx supervisor

# Criar banco de dados
sudo -u postgres psql -c "CREATE DATABASE costadodende_db;"
sudo -u postgres psql -c "CREATE USER costadodende_user WITH PASSWORD 'CostaDende2026';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE costadodende_db TO costadodende_user;"
sudo -u postgres psql -d costadodende_db -c "GRANT ALL ON SCHEMA public TO costadodende_user;"
sudo -u postgres psql -d costadodende_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO costadodende_user;"
sudo -u postgres psql -d costadodende_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO costadodende_user;"

# Criar usuário da aplicação
useradd -m -s /bin/bash costadodende
mkdir -p /home/costadodende/app
```

### 3. Deploy da Aplicação

```bash
# Transferir arquivos
scp costadodende_deploy.tar.gz root@72.61.27.65:/home/costadodende/

# Extrair
cd /home/costadodende
tar -xzf costadodende_deploy.tar.gz -C app/
chown -R costadodende:costadodende /home/costadodende

# Criar virtualenv
python3 -m venv venv
/home/costadodende/venv/bin/pip install --upgrade pip

# Instalar dependências
/home/costadodende/venv/bin/pip install -r /home/costadodende/app/requirements.txt

# Criar arquivo .env
cat > /home/costadodende/app/.env << 'EOF'
DEBUG=False
DJANGO_SECRET_KEY=c0st4d0d3nd3-pr0duct10n-s3cr3t-k3y-1776520692-49e550f11e93b61580d97cf5b39adffe
DJANGO_ALLOWED_HOSTS=postoscostadodende.com.br,www.postoscostadodende.com.br,72.61.27.65,localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=costadodende_db
DB_USER=costadodende_user
DB_PASSWORD=CostaDende2026
DB_HOST=localhost
DB_PORT=5432
TIMEZONE=America/Bahia
EOF

# Migrations
cd /home/costadodende/app
/home/costadodende/venv/bin/python manage.py migrate --settings=config.settings_production

# Coletar estáticos
/home/costadodende/venv/bin/python manage.py collectstatic --noinput --settings=config.settings_production

# Criar superusuário
/home/costadodende/venv/bin/python manage.py shell --settings=config.settings_production << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@postoscostadodende.com.br', 'Admin@Costa2026')
PYEOF
```

### 4. Configurar Supervisor

```bash
# Criar diretório de logs
mkdir -p /var/log/costadodende
chown costadodende:costadodende /var/log/costadodende

# Criar configuração (ver seção Supervisor acima)
# Arquivo: /etc/supervisor/conf.d/costadodende.conf

# Ativar
supervisorctl reread
supervisorctl update
supervisorctl start costadodende
```

### 5. Configurar Nginx

```bash
# Criar configuração (ver seção Nginx acima)
# Arquivo: /etc/nginx/sites-available/costadodende

# Ativar site
ln -sf /etc/nginx/sites-available/costadodende /etc/nginx/sites-enabled/costadodende

# Remover site padrão
rm -f /etc/nginx/sites-enabled/default

# Testar e recarregar
nginx -t
systemctl reload nginx
```

### 6. Configurar Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

---

## 🔍 VERIFICAÇÃO E TESTES

### Testar Aplicação

```bash
# Testar localmente no servidor
curl -I http://localhost
curl -I http://127.0.0.1:8000

# Testar via IP público
curl -I http://72.61.27.65

# Verificar página de login
curl -s http://72.61.27.65/login/ | grep -o '<title>.*</title>'
# Deve retornar: <title>Entrar | Costa do Dendê</title>
```

### Verificar Serviços

```bash
# PostgreSQL
systemctl status postgresql
sudo -u postgres psql -c "\l" | grep costadodende_db

# Nginx
systemctl status nginx
nginx -t

# Supervisor/Gunicorn
supervisorctl status
supervisorctl status costadodende

# Firewall
ufw status verbose
```

### Verificar Logs

```bash
# Gunicorn
tail -f /var/log/costadodende/access.log
tail -f /var/log/costadodende/error.log

# Nginx
tail -f /var/log/nginx/costadodende_access.log
tail -f /var/log/nginx/costadodende_error.log

# PostgreSQL
tail -f /var/log/postgresql/postgresql-16-main.log

# Supervisor
supervisorctl tail -f costadodende stdout
```

---

## 🛠️ MANUTENÇÃO E TROUBLESHOOTING

### Reiniciar Aplicação

```bash
# Método preferido (sem downtime)
supervisorctl restart costadodende

# Ou reiniciar Supervisor inteiro
systemctl restart supervisor
```

### Atualizar Código

```bash
# No servidor local
tar --exclude='*.pyc' --exclude='__pycache__' \
    -czf costadodende_deploy.tar.gz \
    -C /home/davidsonc/development/CostadoDende \
    apps config templates static manage.py passenger_wsgi.py requirements.txt

# Transferir
scp costadodende_deploy.tar.gz root@72.61.27.65:/home/costadodende/

# No VPS
cd /home/costadodende
supervisorctl stop costadodende
rm -rf app/*
tar -xzf costadodende_deploy.tar.gz -C app/
chown -R costadodende:costadodende app/

# Se houver novas dependências
/home/costadodende/venv/bin/pip install -r app/requirements.txt

# Migrations
cd app
/home/costadodende/venv/bin/python manage.py migrate --settings=config.settings_production

# Coletar estáticos (se mudaram)
/home/costadodende/venv/bin/python manage.py collectstatic --noinput --settings=config.settings_production

# Reiniciar
supervisorctl start costadodende
```

### Backup do Banco de Dados

```bash
# Backup
sudo -u postgres pg_dump costadodende_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
sudo -u postgres pg_dump costadodende_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restaurar
sudo -u postgres psql costadodende_db < backup_20260418_140000.sql
```

### Problemas Comuns

**1. Erro 502 Bad Gateway**

```bash
# Verificar se Gunicorn está rodando
supervisorctl status costadodende

# Ver logs
tail -50 /var/log/costadodende/error.log
```

**2. DisallowedHost**

```bash
# Verificar ALLOWED_HOSTS no .env
cat /home/costadodende/app/.env | grep ALLOWED_HOSTS

# Reiniciar após alterar
supervisorctl restart costadodende
```

**3. Erro de Conexão com Banco**

```bash
# Verificar PostgreSQL
systemctl status postgresql
sudo -u postgres psql -c "\l"

# Testar conexão
psql -h localhost -U costadodende_user -d costadodende_db
```

**4. Arquivos Estáticos não Carregam**

```bash
# Recolet ar estáticos
cd /home/costadodende/app
/home/costadodende/venv/bin/python manage.py collectstatic --noinput --settings=config.settings_production

# Verificar permissões
ls -la /home/costadodende/app/staticfiles/

# Verificar configuração Nginx
nginx -t
```

---

## 📝 NOTAS IMPORTANTES

### Segurança

1. ✅ Firewall UFW ativado
2. ✅ PostgreSQL apenas em localhost (não exposto)
3. ✅ Gunicorn apenas em 127.0.0.1 (não exposto)
4. ⚠️ Usuário root com senha - considere usar chave SSH
5. ⚠️ SSL ainda não configurado - aguardando DNS
6. ✅ DEBUG=False em produção
7. ✅ Senhas fortes configuradas

### Melhorias Futuras

- [ ] Configurar DNS para o domínio
- [ ] Ativar SSL/HTTPS com Let's Encrypt
- [ ] Configurar autenticação SSH por chave (desabilitar senha)
- [ ] Implementar backups automáticos do banco de dados
- [ ] Configurar monitoramento (uptime, performance)
- [ ] Configurar logs centralizados
- [ ] Implementar CDN para arquivos estáticos
- [ ] Configurar rate limiting no Nginx
- [ ] Implementar cache (Redis/Memcached)
- [ ] Configurar email SMTP para produção

### Custos Mensais Estimados

- **VPS Hostinger KVM 2:** ~R$ 50-80/mês
- **Domínio .com.br:** ~R$ 40/ano
- **SSL Let's Encrypt:** Gratuito

---

## 📞 CONTATOS E SUPORTE

### Hostinger

- **Site:** https://hostinger.com.br
- **Painel:** https://hpanel.hostinger.com
- **Suporte:** Chat 24/7 no painel

### Domínio

- **Registro.br:** https://registro.br (se .br)
- **Email Admin:** admin@postoscostadodende.com.br

### Responsável Técnico

- **Nome:** Davidson Campos
- **Email:** [adicionar email]
- **Sistema:** Costa do Dendê

---

## 📅 HISTÓRICO DE ALTERAÇÕES

### 2026-04-18 - Deploy Inicial

- ✅ Configuração completa do VPS Ubuntu 24.04 LTS
- ✅ Instalação PostgreSQL 16
- ✅ Instalação Nginx 1.24.0
- ✅ Configuração Python 3.12.3 + virtualenv
- ✅ Deploy aplicação Django 6.0
- ✅ Configuração Gunicorn 3 workers
- ✅ Configuração Supervisor
- ✅ Remoção completa de MySQL/mysqlclient
- ✅ Migrations aplicadas (39 migrations)
- ✅ 139 arquivos estáticos coletados
- ✅ Superusuário admin criado
- ✅ Firewall UFW configurado
- ✅ Aplicação funcionando em http://72.61.27.65
- ⏳ SSL pendente (aguardando DNS)

---

**FIM DA DOCUMENTAÇÃO**

_Última atualização: 18 de Abril de 2026, 11:05 BRT_  
_Versão: 1.0_
