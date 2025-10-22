#!/bin/bash

# 🚀 Script de déploiement LUMEN

echo "🚀 Déploiement LUMEN"
echo "===================="

# Vérifier si on est dans le bon répertoire
if [ ! -f "serveur_simple.py" ]; then
    echo "❌ Ce script doit être exécuté depuis le répertoire LUMEN"
    echo "💡 Assurez-vous d'être dans le bon dossier"
    exit 1
fi

echo "📦 Préparation du déploiement..."

# Créer un package de déploiement
DEPLOY_DIR="lumen_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

echo "📁 Copie des fichiers essentiels..."

# Copier les fichiers HTML
cp *.html "$DEPLOY_DIR/" 2>/dev/null || true

# Vérifier que tous les dashboards sont présents
echo "🔍 Vérification des dashboards dans le déploiement..."
cd "$DEPLOY_DIR"
if [ -f "check_files.sh" ]; then
    chmod +x check_files.sh
    ./check_files.sh
fi

# Si des dashboards sont manquants, les générer
if [ -f "fix_missing_dashboards.sh" ]; then
    chmod +x fix_missing_dashboards.sh
    ./fix_missing_dashboards.sh
fi
cd ..

# Copier les scripts
cp *.sh "$DEPLOY_DIR/" 2>/dev/null || true
cp *.py "$DEPLOY_DIR/" 2>/dev/null || true

# Copier les fichiers de configuration
cp requirements.txt "$DEPLOY_DIR/" 2>/dev/null || true
cp README.md "$DEPLOY_DIR/" 2>/dev/null || true
cp *.md "$DEPLOY_DIR/" 2>/dev/null || true

# Copier les dossiers nécessaires
if [ -d "ml" ]; then
    cp -r ml "$DEPLOY_DIR/"
fi

if [ -d "data" ]; then
    cp -r data "$DEPLOY_DIR/"
fi

if [ -d "explicabilite" ]; then
    cp -r explicabilite "$DEPLOY_DIR/"
fi

if [ -d "monitoring" ]; then
    cp -r monitoring "$DEPLOY_DIR/"
fi

if [ -d "models" ]; then
    cp -r models "$DEPLOY_DIR/"
fi

# Rendre les scripts exécutables
chmod +x "$DEPLOY_DIR"/*.sh

echo "✅ Déploiement créé dans : $DEPLOY_DIR"
echo ""
echo "📋 Instructions pour la machine de destination :"
echo "1. Copiez le dossier '$DEPLOY_DIR' sur la machine cible"
echo "2. cd $DEPLOY_DIR"
echo "3. ./check_files.sh  # Vérifier les fichiers"
echo "4. ./start.sh        # Lancer le projet"
echo ""
echo "🌐 Le projet sera accessible sur le port détecté automatiquement"
