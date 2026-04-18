#!/bin/bash
# ==================================================
# SCRIPT DE DEPLOY RÁPIDO - COSTA DO DENDÊ
# ==================================================
# Execute no servidor SSH após fazer upload dos arquivos

set -e  # Para em caso de erro

echo "🚀 DEPLOY COSTA DO DENDÊ - HOSTINGER"
echo "===================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Erro: manage.py não encontrado!${NC}"
    echo "Execute este script na pasta public_html do projeto"
    exit 1
fi

echo -e "${YELLOW}📂 Diretório atual:${NC} $(pwd)"
echo ""

# Verificar .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "Crie o arquivo .env antes de continuar."
    echo "Use .env.production.example como modelo."
    exit 1
fi

echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
echo ""

# Perguntar pelo virtualenv
read -p "📍 Caminho do virtualenv (ex: ~/virtualenv/public_html/3.11): " VENV_PATH

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtualenv não encontrado em $VENV_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtualenv encontrado${NC}"
echo ""

# Ativar virtualenv
echo "🐍 Ativando virtualenv..."
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✅ Python: $(which python)${NC}"
echo -e "${GREEN}✅ Versão: $(python --version)${NC}"
echo ""

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip -q
echo -e "${GREEN}✅ Pip atualizado${NC}"
echo ""

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# Verificar configuração Django
echo "🔍 Verificando configuração Django..."
python manage.py check
echo -e "${GREEN}✅ Configuração OK${NC}"
echo ""

# Migrations
echo "🗃️  Rodando migrations..."
python manage.py migrate
echo -e "${GREEN}✅ Migrations aplicadas${NC}"
echo ""

# Collectstatic
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Arquivos estáticos coletados${NC}"
echo ""

# Criar diretório tmp para restart
echo "📂 Criando diretório tmp..."
mkdir -p tmp
echo -e "${GREEN}✅ Diretório tmp criado${NC}"
echo ""

# Restart
echo "🔄 Reiniciando aplicação..."
touch tmp/restart.txt
echo -e "${GREEN}✅ Aplicação reiniciada${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Acesse: https://postoscostadodende.com.br/admin"
echo "2. Crie um superusuário se ainda não criou:"
echo "   python manage.py createsuperuser"
echo ""
echo "Comandos úteis:"
echo "- Ver logs: tail -f ~/logs/error.log"
echo "- Reiniciar app: touch ~/public_html/tmp/restart.txt"
echo "- Migrations: python manage.py migrate"
echo "- Collectstatic: python manage.py collectstatic --noinput"
echo ""
