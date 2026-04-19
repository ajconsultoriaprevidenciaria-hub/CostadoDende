#!/bin/bash
# ==================================================
# SCRIPT DE SETUP COMPLETO VPS - COSTA DO DENDÊ
# ==================================================
set -e  # Para em caso de erro

echo "🚀 INICIANDO CONFIGURAÇÃO DO VPS"
echo "=================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variáveis
DOMAIN="postoscostadodende.com.br"
APP_USER="costadodende"
APP_DIR="/home/$APP_USER/app"
DB_NAME="costadodende_db"
DB_USER="costadodende_user"
DB_PASS="CostaDende2026!@#"

echo -e "${YELLOW}📦 Instalando dependências do sistema...${NC}"
apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    supervisor

echo -e "${GREEN}✅ Dependências instaladas${NC}"

echo -e "${YELLOW}👤 Criando usuário da aplicação...${NC}"
if ! id -u $APP_USER > /dev/null 2>&1; then
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✅ Usuário $APP_USER criado${NC}"
else
    echo -e "${GREEN}✅ Usuário $APP_USER já existe${NC}"
fi

echo -e "${YELLOW}🗄️ Configurando PostgreSQL...${NC}"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    sudo -u postgres createdb $DB_NAME
echo -e "${GREEN}✅ Banco $DB_NAME criado${NC}"

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
echo -e "${GREEN}✅ Usuário $DB_USER criado${NC}"

sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'America/Bahia';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
echo -e "${GREEN}✅ Permissões configuradas${NC}"

echo -e "${YELLOW}📁 Criando estrutura de diretórios...${NC}"
mkdir -p $APP_DIR
mkdir -p /var/log/gunicorn
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /var/log/gunicorn
echo -e "${GREEN}✅ Diretórios criados${NC}"

echo -e "${YELLOW}🔥 Configurando firewall...${NC}"
ufw --force enable
ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS
echo -e "${GREEN}✅ Firewall configurado${NC}"

echo "=================================="
echo -e "${GREEN}🎉 SETUP INICIAL CONCLUÍDO!${NC}"
echo "=================================="
echo ""
echo "Próximos passos:"
echo "1. Fazer upload do código para $APP_DIR"
echo "2. Criar virtualenv e instalar dependências"
echo "3. Configurar .env"
echo "4. Rodar migrations"
echo "5. Configurar Nginx + Gunicorn"
echo "6. Configurar SSL"
