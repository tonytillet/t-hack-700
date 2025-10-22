#!/bin/bash

# 🔍 Script de vérification des serveurs LUMEN

echo "🔍 Vérification des serveurs LUMEN..."
echo "====================================="

# Vérifier les processus Python liés à LUMEN
lumen_processes=$(pgrep -f "serveur_simple.py\|serveur_temp.py" 2>/dev/null)

if [ -z "$lumen_processes" ]; then
    echo "✅ Aucun serveur LUMEN en cours d'exécution"
    exit 0
fi

echo "⚠️  Serveurs LUMEN détectés :"
echo "$lumen_processes" | while read pid; do
    if [ ! -z "$pid" ]; then
        echo "   PID $pid : $(ps -p $pid -o command= 2>/dev/null)"
    fi
done

echo ""
echo "🛑 Pour arrêter tous les serveurs LUMEN :"
echo "   pkill -f 'serveur_simple.py\|serveur_temp.py'"
echo ""
echo "🔧 Pour arrêter tous les processus Python :"
echo "   pkill -f python3"
