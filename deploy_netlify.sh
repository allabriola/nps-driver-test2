#!/bin/bash
# Deploy do dashboard_nps_cs_mensal.html para o Netlify
# Uso: bash deploy_netlify.sh

SITE_ID="4fc735c5-1b5c-4fc5-81a7-28d22cbb7850"
HTML_FILE="$(dirname "$0")/dashboard_nps_cs_mensal.html"
ZIP_FILE="$USERPROFILE/deploy_nps.zip"
TOKEN_FILE="$USERPROFILE/.netlify_token"

# Ler token do arquivo (mais seguro que hardcode)
if [ ! -f "$TOKEN_FILE" ]; then
  echo "Token não encontrado. Cole seu Netlify Personal Access Token:"
  read -r TOKEN
  echo "$TOKEN" > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
else
  TOKEN=$(cat "$TOKEN_FILE")
fi

echo "Criando zip..."
python3 -c "
import zipfile, os, sys
html = sys.argv[1]
out  = sys.argv[2]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(html, 'index.html')
    z.writestr('_headers', '/*\n  Content-Type: text/html; charset=utf-8\n')
print('OK')
" "$HTML_FILE" "$ZIP_FILE"

echo "Fazendo deploy..."
RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/zip" \
  --data-binary @"$ZIP_FILE" \
  "https://api.netlify.com/api/v1/sites/$SITE_ID/deploys")

STATE=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state','?'))")
echo "Estado: $STATE"

if [ "$STATE" = "uploaded" ] || [ "$STATE" = "ready" ]; then
  echo "✓ Deploy enviado! Aguarde ~10s e acesse:"
  echo "  https://resilient-mooncake-1bef40.netlify.app"
else
  echo "Erro no deploy. Resposta:"
  echo "$RESULT"
fi
