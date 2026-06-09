#!/bin/bash
# Script para crear los Secrets en GitHub Actions automáticamente
# Uso: bash setup_secrets.sh

set -e

REPO="churoso/monitoreo-sistema-maestro"
TELEGRAM_TOKEN="8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
TELEGRAM_CHAT_ID="7529527522"

echo "📋 Creando Secrets en GitHub..."
echo "Repositorio: $REPO"
echo ""

# Crear TELEGRAM_TOKEN
echo "✏️  Creando TELEGRAM_TOKEN..."
gh secret set TELEGRAM_TOKEN --body "$TELEGRAM_TOKEN" --repo "$REPO"
echo "✅ TELEGRAM_TOKEN creado"
echo ""

# Crear TELEGRAM_CHAT_ID
echo "✏️  Creando TELEGRAM_CHAT_ID..."
gh secret set TELEGRAM_CHAT_ID --body "$TELEGRAM_CHAT_ID" --repo "$REPO"
echo "✅ TELEGRAM_CHAT_ID creado"
echo ""

echo "🎉 ¡Todos los Secrets están listos!"
echo ""
echo "Próximo paso: ve a https://github.com/$REPO/actions"
echo "y ejecuta el workflow 'Monitor Sistema Maestro'"
