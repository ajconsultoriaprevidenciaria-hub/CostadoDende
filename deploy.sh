#!/usr/bin/env bash
# ====================================================
# DEPLOY LOCAL → VPS — Costa do Dendê
# Uso: ./deploy.sh "mensagem do commit"
#      ./deploy.sh          (pede a mensagem interativamente)
# ====================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
VPS_HOST="root@72.61.27.65"
VPS_SCRIPT="/home/costadodende/deploy_vps.sh"

cd "$(dirname "${BASH_SOURCE[0]}")"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Costa do Dendê — Deploy                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Mensagem do commit ────────────────────────────
COMMIT_MSG="${1:-}"
if [ -z "$COMMIT_MSG" ]; then
    echo -ne "${YELLOW}Mensagem do commit: ${NC}"
    read -r COMMIT_MSG
fi
if [ -z "$COMMIT_MSG" ]; then
    echo -e "${RED}❌ Mensagem do commit não pode ser vazia.${NC}"
    exit 1
fi

# ── 2. Commitar se houver mudanças ───────────────────
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}ℹ️  Nenhuma mudança local para commitar.${NC}"
else
    echo -e "${YELLOW}[1/3] Commitando mudanças...${NC}"
    git add .
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✅ Commit criado${NC}"
fi

# ── 3. Push para GitHub ──────────────────────────────
echo -e "${YELLOW}[2/3] Enviando para GitHub...${NC}"
git push origin main
echo -e "${GREEN}✅ Push realizado${NC}"

# ── 4. Enviar deploy_vps.sh se não existir na VPS ────
echo -e "${YELLOW}[3/3] Conectando à VPS...${NC}"
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$VPS_HOST" "test -f $VPS_SCRIPT" 2>/dev/null; then
    echo -e "${YELLOW}   Enviando deploy_vps.sh para o servidor...${NC}"
    scp -o StrictHostKeyChecking=no deploy_vps.sh "$VPS_HOST:$VPS_SCRIPT"
    ssh -o StrictHostKeyChecking=no "$VPS_HOST" "chmod +x $VPS_SCRIPT"
    echo -e "${GREEN}   ✅ deploy_vps.sh instalado na VPS${NC}"
fi

# ── 5. Executar deploy na VPS ────────────────────────
ssh -o StrictHostKeyChecking=no -t "$VPS_HOST" "bash $VPS_SCRIPT"

echo ""
echo -e "${GREEN}✅ Deploy completo!${NC}"
echo -e "   Site: ${BLUE}https://postoscostadodende.com.br${NC}"
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
