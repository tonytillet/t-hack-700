#!/bin/bash

# 🧹 Script de nettoyage LUMEN
echo "🧹 Nettoyage du projet LUMEN..."
echo "================================"

# Arrêter tous les processus Python
echo "🛑 Arrêt des processus Python..."
pkill -f python3 2>/dev/null || true

# Libérer tous les ports utilisés
echo "🔓 Libération des ports..."
lsof -ti:8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090 | xargs kill -9 2>/dev/null || true

# Supprimer les fichiers temporaires (sauf les scripts utiles)
echo "🗑️ Suppression des fichiers temporaires..."
rm -f *.bak *.tmp *.log
rm -f serveur_simple.py.bak serveur_simple.py.tmp
rm -f __pycache__/*.pyc 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true

echo "✅ Nettoyage terminé !"
echo ""
echo "🚀 Vous pouvez maintenant lancer le projet avec :"
echo "   ./start.sh"
echo ""
echo "🌐 Ou directement :"
echo "   python3 serveur_simple.py"