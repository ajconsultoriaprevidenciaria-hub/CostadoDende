# 📋 HISTÓRICO COMPLETO DO DEPLOY - COSTA DO DENDÊ

**Data:** 18/04/2026  
**Status:** ✅ **CONCLUÍDO COM SUCESSO**  
**URL:** https://postoscostadodende.com.br

---

## 🎯 RESUMO EXECUTIVO

Deploy bem-sucedido do sistema Costa do Dendê em VPS Hostinger KVM 2 com Ubuntu 24.04 LTS, PostgreSQL 16, Nginx 1.24.0, e SSL válido. Sistema 100% operacional.

---

## 🖥️ INFRAESTRUTURA FINAL

### **VPS Hostinger KVM 2**

- **Provedor:** Hostinger
- **Plano:** KVM 2 VPS
- **OS:** Ubuntu 24.04.4 LTS
- **Kernel:** 6.8.0-110-generic (requer reboot para ativar)
- **RAM:** 8 GB
- **CPU:** 2 vCPU
- **IPv4:** 72.61.27.65
- **IPv6:** 2a02:4780:6e:5ca9::1

### **Acesso SSH**

```bash
ssh root@72.61.27.65
```

**Senha:** `Vps6558costadodendE@`

---

## 🗄️ BANCO DE DADOS

### **PostgreSQL 16.13**

- **Database:** costadodende_db
- **User:** costadodende_user
- **Password:** CostaDende2026
- **Host:** localhost
- **Port:** 5432

**String de conexão:**

```
postgresql://costadodende_user:CostaDende2026@localhost:5432/costadodende_db
```

---

## 🔐 CREDENCIAIS DO SISTEMA

### **Superusuário Django**

- **Usuário:** admin
- **Senha:** Admin@Costa2026
- **Login:** https://postoscostadodende.com.br/login/

### **Painel Admin**

- **URL:** https://postoscostadodende.com.br/admin/
- **Mesmo login acima**

---

## 🌐 DOMÍNIO E DNS

### **Domínio**

- **Nome:** postoscostadodende.com.br
- **Registro:** 2020-11-12
- **Expiração:** 2035-11-12
- **Proprietário:** Jonathan Ramon Bonfim Fonseca

### **DNS (Hostinger)**

- **Nameserver 1:** pixel.dns-parking.com
- **Nameserver 2:** byte.dns-parking.com
- **Última atualização:** 2026-04-18

### **Registros DNS Configurados**

```
A       @       72.61.27.65               (IPv4 - VPS)
AAAA    @       REMOVIDO                  (IPv6 removido por conflito)
MX      @       mx1.hostinger.com (5)
MX      @       mx2.hostinger.com (10)
```

---

## 🔒 CERTIFICADO SSL

### **Let's Encrypt via Certbot**

- **Domínio:** postoscostadodende.com.br
- **Emissão:** 2026-04-18
- **Expiração:** 2026-07-17 (3 meses)
- **Renovação automática:** Configurada via cron

**Arquivos:**

```
/etc/letsencrypt/live/postoscostadodende.com.br/fullchain.pem
/etc/letsencrypt/live/postoscostadodende.com.br/privkey.pem
```

**⚠️ Pendente:** Certificado para www.postoscostadodende.com.br

---

## 🏗️ STACK TECNOLÓGICA

### **Software Instalado**

| Componente     | Versão      | Status                 |
| -------------- | ----------- | ---------------------- |
| **Ubuntu**     | 24.04.4 LTS | ✅ Ativo               |
| **Python**     | 3.12.3      | ✅ Ativo               |
| **Django**     | 6.0.4       | ✅ Rodando             |
| **PostgreSQL** | 16.13       | ✅ Ativo               |
| **Nginx**      | 1.24.0      | ✅ Ativo               |
| **Gunicorn**   | 23.0.0      | ✅ Rodando (pid 24583) |
| **Supervisor** | 4.2.5       | ✅ Gerenciando         |
| **Certbot**    | 2.9.0       | ✅ SSL ativo           |

### **Dependências Python**

```
django==6.0.4
psycopg2-binary==2.9.11
python-dotenv==1.2.2
plotly==6.7.0
pandas==3.0.2
reportlab==4.4.10
Pillow==12.2.0
whitenoise==6.12.0
gunicorn==23.0.0
```

**❌ MySQL:** Completamente removido conforme solicitação do usuário

---

## 📁 ESTRUTURA DE ARQUIVOS

### **Aplicação**

```
/home/costadodende/app/          # Código Django
/home/costadodende/venv/         # Virtualenv Python 3.12.3
/home/costadodende/app/.env      # Variáveis de ambiente
```

### **Arquivos Estáticos**

```
/home/costadodende/app/staticfiles/    # 139 arquivos coletados
```

### **Permissões**

```bash
/home/costadodende/             755 (costadodende:costadodende)
/home/costadodende/app/         755 (costadodende:costadodende)
/home/costadodende/staticfiles/ 755 (costadodende:costadodende)
```

---

## ⚙️ CONFIGURAÇÕES DO SERVIDOR

### **Nginx** (`/etc/nginx/sites-available/costadodende`)

**3 Server Blocks configurados:**

1. **HTTPS (porta 443)** - Certificado SSL
   - Domínio + IP: postoscostadodende.com.br, www, 72.61.27.65
   - Proxy reverso para 127.0.0.1:8000
   - Serve arquivos estáticos diretamente

2. **HTTP Redirect (porta 80)** - Apenas domínio
   - Redireciona http → https para domínio

3. **HTTP Direto (porta 80)** - Para IP
   - Permite acesso via http://72.61.27.65
   - Sem redirect (útil para testes)

### **Gunicorn** (gerenciado pelo Supervisor)

```
Workers: 3
Bind: 127.0.0.1:8000
User: costadodende
Working Dir: /home/costadodende/app
```

### **Supervisor** (`/etc/supervisor/conf.d/costadodende.conf`)

```
[program:costadodende]
command=/home/costadodende/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/home/costadodende/app
user=costadodende
autostart=true
autorestart=true
```

**Status atual:**

```
Process: costadodende
PID: 24583
Uptime: 5+ horas
Status: RUNNING
```

### **Firewall (UFW)**

```
22/tcp    ALLOW    SSH
80/tcp    ALLOW    HTTP
443/tcp   ALLOW    HTTPS
```

---

## 🔧 VARIÁVEIS DE AMBIENTE (.env)

```bash
# Segurança
DEBUG=False
DJANGO_SECRET_KEY=[gerado automaticamente]

# Hosts permitidos
DJANGO_ALLOWED_HOSTS=postoscostadodende.com.br,www.postoscostadodende.com.br,72.61.27.65

# Banco de dados
DATABASE_URL=postgresql://costadodende_user:CostaDende2026@localhost:5432/costadodende_db

# Timezone
TIMEZONE=America/Bahia
```

---

## 🛠️ CONFIGURAÇÕES DJANGO

### **settings_production.py** (Configurações importantes)

```python
DEBUG = False

# ⚠️ TEMPORARIAMENTE DESATIVADO para acesso via HTTP no IP
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# TODO: Reativar quando 100% em HTTPS

ALLOWED_HOSTS = [
    'postoscostadodende.com.br',
    'www.postoscostadodende.com.br',
    '72.61.27.65',
]

CSRF_TRUSTED_ORIGINS = [
    'https://postoscostadodende.com.br',
    'https://www.postoscostadodende.com.br',
    'http://postoscostadodende.com.br',
    'http://72.61.27.65',
    'https://72.61.27.65',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... configurado via DATABASE_URL
    }
}
```

---

## 📖 HISTÓRICO DE PROBLEMAS E SOLUÇÕES

### ❌ **Problema 1: Shared Hosting sem Python**

**Sintoma:** Hostinger shared hosting não suporta Python/Django  
**Solução:** Migração para VPS Hostinger KVM 2  
**Data:** 2026-04-18

### ❌ **Problema 2: MySQL não desejado**

**Sintoma:** Projeto originalmente configurado com MySQL  
**Solução:** Remoção completa do mysqlclient, migração para PostgreSQL 16  
**Data:** 2026-04-18

### ❌ **Problema 3: Registro IPv6 AAAA apontando para servidor antigo**

**Sintoma:** Após remoção do site da shared hosting e atualização do DNS IPv4, o domínio ainda retornava "Server: LiteSpeed" em vez de nginx  
**Causa raiz:** DNS tinha registro AAAA (IPv6) apontando para `2a02:4780:13:914:0:3a53:449e:5` (servidor antigo). Navegadores modernos preferem IPv6 quando disponível.  
**Diagnóstico:**

```bash
# IPv4 funcionava
curl -4 -I https://postoscostadodende.com.br  # ✅ nginx

# IPv6 falhava
curl -6 -I https://postoscostadodende.com.br  # ❌ LiteSpeed
```

**Solução:** Remoção do registro AAAA no painel DNS da Hostinger  
**Resultado:** Propagação em 5-15 minutos  
**Data:** 2026-04-18 ~19:50

### ❌ **Problema 4: Cache DNS local persistente**

**Sintoma:** Após remoção do AAAA, DNS oficial não tinha mais o registro mas computador local ainda retornava IPv6 antigo  
**Solução:**

```bash
sudo resolvectl flush-caches
# OU
echo "72.61.27.65 postoscostadodende.com.br" | sudo tee -a /etc/hosts
```

**Data:** 2026-04-18 ~20:00

### ❌ **Problema 5: Static files 404**

**Sintoma:** Dashboard carregava sem CSS/estilos  
**Causa:** Permissões em /home/costadodende (750) bloqueavam nginx  
**Solução:**

```bash
chmod 755 /home/costadodende
chown -R costadodende:costadodende /home/costadodende/app/staticfiles
python manage.py collectstatic --noinput  # 139 arquivos
```

**Data:** 2026-04-18

### ❌ **Problema 6: Login não funcionava via HTTP**

**Sintoma:** Cookies não eram salvos em http://72.61.27.65  
**Causa:** SESSION_COOKIE_SECURE=True requer HTTPS  
**Solução temporária:** Desativado SESSION_COOKIE_SECURE e CSRF_COOKIE_SECURE  
**TODO:** Reativar após confirmar 100% HTTPS  
**Data:** 2026-04-18

---

## 🎨 FUNCIONALIDADES IMPLEMENTADAS

### **Landing Page Pública**

- **URL:** https://postoscostadodende.com.br/ (usuários não autenticados)
- **Template:** templates/core/landing.html
- **Features:**
  - Hero section com background
  - Estatísticas da rede
  - Cards de serviços (Diesel S10, Gasolina, Etanol, GNV)
  - Botão de CTA para login
  - Design responsivo com tema escuro

### **Redirect Inteligente**

```python
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return LandingPageView.as_view()(request)
```

### **Rotas Configuradas**

- `/` → Landing page (anônimos) ou Dashboard (autenticados)
- `/login/` → Sistema de login
- `/admin/` → Painel administrativo Django
- `/dashboard/` → Dashboard principal (requer login)
- `/estoque/` → Gestão de estoque (do Ramon)
- `/sobre/` → Landing page explícita

---

## 🔄 COMANDOS ÚTEIS DE MANUTENÇÃO

### **Reiniciar serviços**

```bash
ssh root@72.61.27.65

# Reiniciar Gunicorn via Supervisor
supervisorctl restart costadodende
supervisorctl status costadodende

# Reiniciar Nginx
systemctl restart nginx
systemctl status nginx

# Reiniciar PostgreSQL
systemctl restart postgresql
systemctl status postgresql
```

### **Ver logs**

```bash
# Logs do Gunicorn/Django
tail -f /var/log/supervisor/costadodende-stderr.log
tail -f /var/log/supervisor/costadodende-stdout.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs do PostgreSQL
tail -f /var/log/postgresql/postgresql-16-main.log
```

### **Atualizar código**

```bash
# No servidor
cd /home/costadodende/app
source /home/costadodende/venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
supervisorctl restart costadodende
```

### **Backup do banco**

```bash
# Criar backup
pg_dump -U costadodende_user costadodende_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
psql -U costadodende_user costadodende_db < backup_20260418_200000.sql
```

---

## ✅ CHECKLIST DE DEPLOY CONCLUÍDO

- [x] VPS provisionado e configurado
- [x] Ubuntu 24.04 LTS atualizado (32 pacotes)
- [x] PostgreSQL 16 instalado e database criada
- [x] MySQL completamente removido
- [x] Python 3.12.3 + virtualenv configurado
- [x] Dependências instaladas (sem MySQL)
- [x] Nginx 1.24.0 instalado e configurado (3 server blocks)
- [x] Certificado SSL obtido (Let's Encrypt)
- [x] Gunicorn configurado (3 workers)
- [x] Supervisor instalando gerenciando Gunicorn
- [x] 39 migrations aplicadas
- [x] 139 static files coletados
- [x] Superuser criado (admin)
- [x] UFW firewall configurado (22, 80, 443)
- [x] Landing page implementada
- [x] DNS A record configurado (72.61.27.65)
- [x] DNS AAAA record removido (conflito resolvido)
- [x] Código sincronizado com GitHub (conflitos resolvidos)
- [x] Documentação completa criada
- [x] Site 100% operacional

---

## 🚀 MELHORIAS PENDENTES (Opcional)

### **Alta Prioridade**

1. ⚠️ **Re-ativar cookies seguros**
   - SESSION_COOKIE_SECURE = True
   - CSRF_COOKIE_SECURE = True
   - (Aguardando confirmar 100% HTTPS)

2. 🔄 **Reiniciar VPS**
   - Ativar kernel 6.8.0-110-generic
   - Comando: `reboot`

### **Média Prioridade**

3. 🌐 **Adicionar certificado SSL para www**

   ```bash
   certbot --nginx -d www.postoscostadodende.com.br
   ```

4. 💾 **Configurar backups automáticos**
   - Cron job diário para PostgreSQL
   - Retenção: 7 dias
   - Local: /home/costadodende/backups/

5. 📧 **Configurar email**
   - Integrar com serviço de email Hostinger
   - Configurar SMTP para notificações Django

### **Baixa Prioridade**

6. 📊 **Monitoramento**
   - Log rotation (logrotate)
   - Alertas de espaço em disco
   - Monitoramento de uptime

7. 🔒 **Hardening de segurança**
   - Fail2ban para SSH
   - Rate limiting no Nginx
   - Backup de .env em local seguro

---

## 📞 SUPORTE E CONTATOS

### **Hostinger Support**

- Website: https://hpanel.hostinger.com
- Chat: Disponível 24/7
- Email: support@hostinger.com

### **Repositório GitHub**

- Repo: ajconsultoriaprevidenciaria-hub/CostadoDende
- Branch: main
- Última sincronização: 2026-04-18

---

## 📝 NOTAS FINAIS

✅ **Deploy bem-sucedido após superar desafios técnicos:**

1. Migração de shared hosting para VPS
2. Remoção completa do MySQL
3. Resolução de conflito IPv6/DNS
4. Integração de mudanças do GitHub (Ramon)
5. Landing page pública implementada

🎉 **Sistema 100% operacional e acessível mundialmente!**

**Última atualização:** 2026-04-18 20:02 BRT  
**Responsável:** Davidson (com assistência da IA)  
**Status:** PRODUÇÃO ✅
