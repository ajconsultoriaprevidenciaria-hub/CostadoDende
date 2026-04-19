#!/usr/bin/env bash
# ====================================================
# START LOCAL — Costa do Dendê
# Uso    : ./start_local.sh
# Detecta se é a primeira vez (sem .venv) ou uso diário.
# ====================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Costa do Dendê — Start Local           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── PRIMEIRA VEZ: .venv ainda não existe ────────────
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚡ Primeira execução detectada. Configurando ambiente...${NC}"
    echo ""

    # Criar ambiente virtual
    python3 -m venv .venv
    echo -e "${GREEN}✅ Ambiente virtual criado (.venv)${NC}"

    source .venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependências instaladas${NC}"

    # Criar .env local mínimo se não existir
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
DEBUG=True
DJANGO_SECRET_KEY=local-dev-secret-key-nao-usar-em-producao
DB_ENGINE=django.db.backends.sqlite3
EOF
        echo -e "${YELLOW}⚠️  .env criado com SQLite local (valores de dev)${NC}"
    else
        echo -e "${GREEN}✅ .env já existe${NC}"
    fi

    # Migrations + estáticos iniciais
    python manage.py migrate
    python manage.py collectstatic --noinput -v 0
    echo -e "${GREEN}✅ Banco e arquivos estáticos prontos${NC}"

    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  Crie seu superusuário para acessar /admin/${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    python manage.py createsuperuser
    echo ""

# ── DIA A DIA: .venv já existe ──────────────────────
else
    source .venv/bin/activate

    # Garante que dependências do requirements.txt estejam instaladas
    pip install -r requirements.txt -q

    # Aplica migrations pendentes silenciosamente
    PENDING=$(python manage.py showmigrations --plan 2>/dev/null | grep -c "\[ \]" || true)
    PENDING=${PENDING:-0}
    if [ "${PENDING}" -gt 0 ] 2>/dev/null; then
        echo -e "${YELLOW}⚡ $PENDING migration(s) pendente(s). Aplicando...${NC}"
        python manage.py migrate
        echo -e "${GREEN}✅ Migrations aplicadas${NC}"
    else
        echo -e "${GREEN}✅ Banco de dados atualizado${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🚀 Servidor iniciando...${NC}"
echo -e "   App  : ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "   Admin: ${BLUE}http://127.0.0.1:8000/admin/${NC}"
echo -e "   Ctrl+C para parar"
echo ""
python manage.py runserver
