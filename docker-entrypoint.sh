#!/bin/bash

# 🐳 Script d'entrée Docker pour LUMEN

echo "🐳 LUMEN - Démarrage Docker"
echo "============================"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1

# Vérifier et réparer les dashboards
echo "🔍 Vérification des dashboards..."
./check_files.sh

# Si des dashboards sont manquants, les réparer
if [ -f "fix_missing_dashboards.sh" ]; then
    echo "🔧 Réparation automatique des dashboards manquants..."
    ./fix_missing_dashboards.sh
fi

# Démarrer le serveur
echo "🚀 Démarrage du serveur LUMEN sur le port $LUMEN_PORT..."

# Modifier le port dans le serveur
sed -i "s/PORT = [0-9]*/PORT = $LUMEN_PORT/" serveur_simple.py

# Lancer le serveur
python3 serveur_simple.py
