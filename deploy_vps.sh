#!/usr/bin/env bash
# ====================================================
# DEPLOY VPS — Costa do Dendê
# Roda DENTRO DO SERVIDOR VPS.
# Chamado remotamente pelo deploy.sh local.
# Usa reload GRACIOSO do Gunicorn: zero downtime.
# ====================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
APP_DIR="/home/costadodende/app"
VENV="/home/costadodende/venv"
SETTINGS="config.settings_production"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Costa do Dendê — Deploy VPS            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo -e "   $(date '+%d/%m/%Y %H:%M:%S UTC')"
echo ""

cd "$APP_DIR"
source "$VENV/bin/activate"

# ── 1. Puxar código atualizado do GitHub ────────────
echo -e "${YELLOW}[1/5] Atualizando código...${NC}"
git fetch origin main
git reset --hard origin/main
echo -e "${GREEN}✅ $(git log -1 --format='%h — %s')${NC}"

# ── 2. Dependências ──────────────────────────────────
echo -e "${YELLOW}[2/5] Verificando dependências...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependências verificadas${NC}"

# ── 3. Migrations ────────────────────────────────────
echo -e "${YELLOW}[3/5] Aplicando migrations...${NC}"
python manage.py migrate --settings="$SETTINGS"
echo -e "${GREEN}✅ Migrations aplicadas${NC}"

# ── 4. Arquivos estáticos ────────────────────────────
echo -e "${YELLOW}[4/5] Coletando estáticos...${NC}"
python manage.py collectstatic --noinput -v 0 --settings="$SETTINGS"
echo -e "${GREEN}✅ Estáticos coletados${NC}"

# ── 5. Reload GRACIOSO do Gunicorn ───────────────────
# SIGHUP ao master do Gunicorn: novos workers sobem ANTES dos
# antigos descerem. Requisições em andamento terminam normalmente.
# Usuários ativos não percebem nada — zero downtime.
echo -e "${YELLOW}[5/5] Recarregando Gunicorn (graceful reload)...${NC}"
supervisorctl signal HUP costadodende
sleep 3

STATUS=$(supervisorctl status costadodende)
if echo "$STATUS" | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ $STATUS${NC}"
else
    echo -e "${RED}⚠️  Status inesperado: $STATUS${NC}"
    echo -e "${RED}   Verifique: supervisorctl tail costadodende stderr${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Deploy concluído com sucesso!${NC}"
echo -e "   Site: ${BLUE}https://postoscostadodende.com.br${NC}"
echo ""
