#!/bin/bash

# 🚨 Script d'installation automatique - Système d'alerte grippe France
# Usage: ./install.sh

echo "🚨 Installation du système d'alerte grippe France"
echo "=================================================="

# Vérification de Python
echo "📋 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION détecté"

# Vérification de pip
echo "📋 Vérification de pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi
echo "✅ pip3 détecté"

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
echo "✅ Dépendances installées"

# Création des dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p data/spf data/insee data/meteo data/wikipedia data/google_trends data/processed data/alerts models

# Collecte des données
echo "📊 Collecte des données..."
python3 scripts/collect_real_data_fixed.py

if [ $? -ne 0 ]; then
    echo "⚠️  Erreur lors de la collecte des données, mais on continue..."
fi

# Fusion des données
echo "🔄 Fusion des données..."
python3 scripts/fuse_data.py

if [ $? -ne 0 ]; then
    echo "⚠️  Erreur lors de la fusion des données, mais on continue..."
fi

# Génération des alertes
echo "🚨 Génération des alertes..."
python3 scripts/create_alert_system.py

if [ $? -ne 0 ]; then
    echo "⚠️  Erreur lors de la génération des alertes, mais on continue..."
fi

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "🚀 Pour lancer l'application :"
echo "   python3 launch_app.py"
echo ""
echo "🌐 L'application sera accessible sur :"
echo "   http://localhost:8501"
echo ""
echo "📚 Pour plus d'informations, consultez le README.md"
