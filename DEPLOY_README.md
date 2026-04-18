# 🚀 Deploy em Produção - Costa do Dendê

**Status:** ✅ Em Produção  
**URL:** https://postoscostadodende.com.br  
**Data de Deploy:** 18/04/2026

---

## 📋 Visão Geral

Sistema Costa do Dendê deployado com sucesso em VPS com stack moderna e segura.

---

## 🏗️ Stack Tecnológica

| Componente              | Versão           | Descrição                    |
| ----------------------- | ---------------- | ---------------------------- |
| **Sistema Operacional** | Ubuntu 24.04 LTS | Base do servidor             |
| **Python**              | 3.12.3           | Runtime da aplicação         |
| **Django**              | 6.0.4            | Framework web                |
| **PostgreSQL**          | 16.13            | Banco de dados principal     |
| **Nginx**               | 1.24.0           | Servidor web / Proxy reverso |
| **Gunicorn**            | 23.0.0           | Application server WSGI      |
| **Supervisor**          | 4.2.5            | Gerenciador de processos     |
| **Certbot**             | 2.9.0            | Certificados SSL             |

**Nota:** MySQL foi completamente removido do projeto.

---

## 🔧 Arquitetura

```
Internet
    ↓
[Nginx :80, :443] → SSL/TLS, Static Files
    ↓
[Gunicorn :8000] → 3 workers
    ↓
[Django Application]
    ↓
[PostgreSQL :5432]
```

---

## 📁 Estrutura de Diretórios

```
/home/costadodende/
├── app/                    # Código Django
│   ├── apps/              # Aplicações Django
│   ├── config/            # Configurações
│   ├── static/            # Arquivos estáticos (source)
│   ├── staticfiles/       # Arquivos estáticos (coletados)
│   ├── templates/         # Templates HTML
│   ├── manage.py
│   ├── requirements.txt
│   └── .env              # Variáveis de ambiente (não versionado)
└── venv/                  # Virtual environment Python
```

---

## 🌐 Configuração DNS

**Domínio:** postoscostadodende.com.br

### Registros DNS

- **A Record:** Aponta para IP do VPS
- **MX Records:** Configurados para email Hostinger

**Observação importante:** Registro AAAA (IPv6) foi removido para evitar conflitos de roteamento.

---

## 🔒 Segurança

### SSL/TLS

- Certificado Let's Encrypt válido
- Renovação automática configurada
- HTTPS obrigatório para domínio principal

### Firewall

```
Porta 22  (SSH)   - Permitida
Porta 80  (HTTP)  - Permitida (redirect para HTTPS)
Porta 443 (HTTPS) - Permitida
```

### Django Security Settings

```python
DEBUG = False
SESSION_COOKIE_SECURE = False  # TODO: Ativar após 100% HTTPS
CSRF_COOKIE_SECURE = False     # TODO: Ativar após 100% HTTPS
ALLOWED_HOSTS = [domínio, www, IP]
```

---

## 🎨 Funcionalidades

### Landing Page

- Página pública acessível para visitantes não autenticados
- Design responsivo com tema escuro
- Call-to-action para login
- Informações sobre serviços e estatísticas

### Sistema de Autenticação

- Login/logout completo
- Redirecionamento inteligente (landing page vs dashboard)
- Painel administrativo Django

### Dashboard

- Acesso restrito a usuários autenticados
- Gestão de fretes, motoristas, abastecimentos
- Relatórios e estatísticas

---

## 📊 Serviços e Processos

### Supervisor

Gerencia o Gunicorn automaticamente:

- Autostart: Sim
- Autorestart: Sim
- Workers: 3

### Nginx

3 Server Blocks configurados:

1. HTTPS (porta 443) - SSL ativo
2. HTTP redirect (porta 80) - Redireciona para HTTPS
3. HTTP direto para IP (porta 80) - Testes e acesso direto

---

## 🔄 Workflow de Deploy

### Atualização de Código

```bash
# 1. Conectar ao servidor
ssh [usuário]@[servidor]

# 2. Navegar para diretório da aplicação
cd /home/costadodende/app

# 3. Ativar virtualenv
source /home/costadodende/venv/bin/activate

# 4. Atualizar código
git pull origin main

# 5. Instalar dependências
pip install -r requirements.txt

# 6. Aplicar migrações
python manage.py migrate

# 7. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 8. Reiniciar aplicação
sudo supervisorctl restart costadodende

# 9. Verificar status
sudo supervisorctl status costadodende
```

---

## 📝 Logs

### Aplicação (Django/Gunicorn)

```bash
tail -f /var/log/supervisor/costadodende-stderr.log
tail -f /var/log/supervisor/costadodende-stdout.log
```

### Servidor Web (Nginx)

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Banco de Dados (PostgreSQL)

```bash
tail -f /var/log/postgresql/postgresql-16-main.log
```

---

## 🐛 Problemas Conhecidos e Soluções

### Problema: Site ainda mostra servidor antigo após atualizar DNS

**Causa:** Cache DNS local  
**Solução:**

```bash
# Linux
sudo resolvectl flush-caches

# Ou adicionar ao /etc/hosts
echo "[IP] postoscostadodende.com.br" | sudo tee -a /etc/hosts
```

### Problema: Static files retornando 404

**Causa:** Permissões incorretas ou collectstatic não executado  
**Solução:**

```bash
python manage.py collectstatic --noinput
sudo chown -R costadodende:costadodende /home/costadodende/app/staticfiles
sudo chmod 755 /home/costadodende
```

### Problema: Gunicorn não inicia

**Causa:** Erro no código Python ou configuração  
**Diagnóstico:**

```bash
sudo supervisorctl status costadodende
sudo tail -f /var/log/supervisor/costadodende-stderr.log
```

---

## 📦 Backup

### Banco de Dados

```bash
# Criar backup
pg_dump -U [usuario] [database] > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
psql -U [usuario] [database] < backup_YYYYMMDD_HHMMSS.sql
```

### Código e Configurações

- Código versionado no GitHub
- Configurações salvas em /etc/nginx e /etc/supervisor/conf.d
- Arquivo .env mantido fora do repositório

---

## ✅ Checklist de Manutenção

**Diário:**

- [ ] Verificar logs de erro
- [ ] Confirmar site acessível

**Semanal:**

- [ ] Verificar uso de disco
- [ ] Backup do banco de dados
- [ ] Verificar logs de acesso (tráfego)

**Mensal:**

- [ ] Atualizar pacotes do sistema (`apt update && apt upgrade`)
- [ ] Verificar validade do certificado SSL
- [ ] Revisar logs de segurança

**Trimestral:**

- [ ] Revisar performance
- [ ] Otimizar banco de dados
- [ ] Atualizar documentação

---

## 🚀 Melhorias Futuras

### Planejadas

- [ ] Re-ativar SESSION_COOKIE_SECURE e CSRF_COOKIE_SECURE
- [ ] Adicionar certificado SSL para www subdomain
- [ ] Configurar backups automáticos (cron)
- [ ] Implementar monitoramento de uptime
- [ ] Configurar log rotation

### Consideradas

- [ ] CDN para static files
- [ ] Redis para cache
- [ ] Monitoramento com Sentry ou similar
- [ ] CI/CD com GitHub Actions
- [ ] Ambiente de staging

---

## 📚 Referências

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

## 📞 Suporte

**Repositório GitHub:** ajconsultoriaprevidenciaria-hub/CostadoDende  
**Branch Principal:** main

Para credenciais e informações sensíveis, consulte o arquivo **DEPLOY_PRODUCAO_HISTORICO.md** (não versionado).

---

**Última atualização:** 2026-04-18  
**Versão:** 1.0.0  
**Status:** ✅ Produção
