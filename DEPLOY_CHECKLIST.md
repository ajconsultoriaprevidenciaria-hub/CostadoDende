# ✅ CHECKLIST DE DEPLOY - HOSTINGER

Use este checklist para garantir que nada foi esquecido.

---

## PRÉ-DEPLOY (Local)

- [ ] Código testado localmente (`python manage.py runserver`)
- [ ] Migrations criadas (`python manage.py makemigrations`)
- [ ] Requirements.txt atualizado
- [ ] Arquivos estáticos OK (`python manage.py collectstatic`)
- [ ] `.gitignore` configurado (não sobe `.env`, `db.sqlite3`, etc)
- [ ] Código commitado no Git

---

## PAINEL HOSTINGER

- [ ] Banco de dados MySQL criado
  - Nome: `u978535582_costadodende`
  - Usuário: `u978535582_costadodende`
  - Senha: ********\_\_\_********
  - Host: `localhost`

- [ ] Aplicativo Python configurado
  - Versão: Python 3.11+
  - Diretório: `public_html`
  - Arquivo inicial: `passenger_wsgi.py`
  - URL: `postoscostadodende.com.br`

- [ ] SSL/HTTPS habilitado
  - Let's Encrypt ativado
  - Certificado válido

---

## SERVIDOR SSH

- [ ] Conectado via SSH: `ssh -p 65002 u978535582@82.180.153.36`

- [ ] Arquivos enviados para `~/public_html/`
  - apps/
  - config/
  - templates/
  - static/
  - manage.py
  - passenger_wsgi.py
  - requirements.txt

- [ ] Arquivo `.env` criado e configurado
  - DJANGO_SECRET_KEY gerada
  - DB_NAME, DB_USER, DB_PASSWORD corretos
  - ALLOWED_HOSTS configurados
  - DEBUG=False

- [ ] Virtualenv ativado
  - `source ~/virtualenv/public_html/3.11/bin/activate`

- [ ] Dependências instaladas
  - `pip install -r requirements.txt`
  - Sem erros

- [ ] Django check OK
  - `python manage.py check`
  - Sem warnings críticos

- [ ] Migrations aplicadas
  - `python manage.py migrate`
  - Todas as tabelas criadas

- [ ] Superusuário criado
  - `python manage.py createsuperuser`
  - Usuário: ********\_\_\_********
  - Senha: ********\_\_\_********

- [ ] Arquivos estáticos coletados
  - `python manage.py collectstatic --noinput`
  - Pasta `staticfiles/` populada

- [ ] Aplicação reiniciada
  - `touch tmp/restart.txt`

---

## TESTES NO SITE

- [ ] Site carrega: https://postoscostadodende.com.br
  - Sem erro 500
  - Sem erro 404
  - Página inicial OK

- [ ] Admin carrega: https://postoscostadodende.com.br/admin
  - Login funciona
  - Painel admin OK
  - CSS/JS carregando

- [ ] HTTPS funciona
  - Cadeado verde
  - Certificado válido
  - Sem avisos de segurança

- [ ] Funcionalidades testadas
  - Login/Logout
  - CRUD de dados
  - Upload de arquivos (se aplicável)
  - Relatórios/Dashboard

---

## PÓS-DEPLOY

- [ ] Backup do banco criado
  - `mysqldump -u USER -p DATABASE > backup.sql`

- [ ] Logs verificados
  - `tail -50 ~/logs/error.log`
  - Sem erros críticos

- [ ] Monitoramento configurado
  - Uptime Robot / Similar
  - Alertas de erro

- [ ] Documentação atualizada
  - README.md
  - CHANGELOG.md
  - Credenciais em local seguro

- [ ] Usuários/Cliente notificados
  - Site no ar
  - Credenciais enviadas
  - Treinamento agendado

---

## COMANDOS RÁPIDOS

```bash
# Conectar SSH
ssh -p 65002 u978535582@82.180.153.36

# Ativar virtualenv
source ~/virtualenv/public_html/3.11/bin/activate

# Reiniciar app
touch ~/public_html/tmp/restart.txt

# Ver logs
tail -50 ~/logs/error.log

# Backup banco
mysqldump -u u978535582_costadodende -p u978535582_costadodende > backup_$(date +%Y%m%d).sql
```

---

**🎯 OBJETIVO: TODOS OS ITENS MARCADOS!**
