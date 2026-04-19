# Costa do Dendê - Sistema de Gestão

Sistema de gestão integrado para controle de fretes, motoristas, abastecimentos e operações dos Postos Costa do Dendê.

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# Primeira execução ou setup completo
./scripts/start_local.sh

# Uso diário
./scripts/start_local.sh
```

O script `start_local.sh` detecta automaticamente se é a primeira execução e:

- Cria ambiente virtual Python
- Instala dependências
- Executa migrações
- Cria superusuário (primeira vez)
- Inicia servidor de desenvolvimento

### Deploy em Produção

```bash
# Deploy completo (local → VPS)
./scripts/deploy.sh "mensagem do commit"
```

O script automatiza:

- Commit e push para GitHub
- Deploy no servidor VPS
- Migrações de banco de dados
- Coleta de arquivos estáticos
- Reload graceful do Gunicorn (zero downtime)

## 📁 Estrutura do Projeto

```
CostadoDende/
├── apps/                      # Aplicações Django
│   ├── core/                  # App principal
│   ├── dashboard/             # Dashboard administrativo
│   ├── fretes/                # Gestão de fretes
│   └── motorista_portal/      # Portal do motorista
├── config/                    # Configurações Django
│   ├── settings.py            # Settings desenvolvimento
│   └── settings_production.py # Settings produção
├── docs/                      # Documentação
│   ├── deployment/            # Guias de deploy
│   ├── development/           # Guias de desenvolvimento
│   └── installer/             # Documentação instalador
├── scripts/                   # Scripts de automação
│   ├── deploy.sh              # Deploy automatizado
│   ├── deploy_vps.sh          # Script rodado no VPS
│   ├── start_local.sh         # Setup desenvolvimento local
│   └── vps_setup.sh           # Setup inicial VPS
├── static/                    # Arquivos estáticos (desenvolvimento)
├── staticfiles/               # Arquivos estáticos coletados
├── templates/                 # Templates Django
└── manage.py                  # Django management
```

## 🛠 Stack Tecnológico

- **Backend:** Django 6.0.4, Python 3.12
- **Banco de Dados:** PostgreSQL 16 (produção), SQLite (desenvolvimento)
- **Web Server:** Nginx 1.24.0 + Gunicorn 23.0.0
- **Process Manager:** Supervisor 4.2.5
- **Infraestrutura:** VPS Hostinger KVM 2, Ubuntu 24.04 LTS
- **Domínio:** https://postoscostadodende.com.br
- **SSL:** Let's Encrypt (Certbot)

## 📝 Aplicações

### Core

Aplicação principal com funcionalidades base do sistema.

### Dashboard

Dashboard administrativo com métricas e visualizações.

### Fretes

Gestão completa de fretes, cargas, rotas e clientes.

### Motorista Portal

Portal para motoristas com acesso a:

- Abastecimentos
- Fretes atribuídos
- Comprovantes
- Histórico

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
# Criar novas migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar testes
python manage.py test

# Shell Django
python manage.py shell
```

### Produção

```bash
# Verificar status do Gunicorn
ssh root@72.61.27.65 'supervisorctl status costadodende'

# Ver logs do Gunicorn
ssh root@72.61.27.65 'tail -f /home/costadodende/logs/gunicorn.log'

# Ver logs do Nginx
ssh root@72.61.27.65 'tail -f /var/log/nginx/error.log'
```

## 📚 Documentação

- **Deployment:** Veja `docs/deployment/` para guias completos de deploy
- **CHANGELOG:** Histórico de mudanças em `CHANGELOG.md`
- **Development:** Configuração de ambiente em `docs/development/`

## 🔐 Segurança

- Credenciais sensíveis em variáveis de ambiente
- SSL/TLS via Let's Encrypt
- Cache desabilitado em desenvolvimento e produção (DummyCache)
- Proteção CSRF ativa
- Debug desabilitado em produção

## 🚀 Deploy

O sistema utiliza deploy automatizado com zero downtime:

1. **Local:** `./scripts/deploy.sh "mensagem"`
2. **GitHub:** Push automático
3. **VPS:** Pull, migrações, collectstatic
4. **Reload:** Gunicorn graceful reload (SIGHUP)

Veja documentação completa em `docs/deployment/DEPLOY_README.md`

## 📄 Licença

Projeto proprietário - Costa do Dendê © 2024-2026

## 👥 Equipe

Desenvolvido por AJ Consultoria Previdenciária
