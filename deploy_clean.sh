#!/bin/bash

# 🚀 Script de déploiement propre et optimisé

echo "🚀 Déploiement LUMEN - Version Propre"
echo "===================================="

# Vérifier si on est dans le bon répertoire
if [ ! -f "serveur_simple.py" ]; then
    echo "❌ Ce script doit être exécuté depuis le répertoire LUMEN"
    exit 1
fi

echo "📦 Création du package de déploiement propre..."

# Créer un package de déploiement
DEPLOY_DIR="lumen_clean_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

echo "📁 Copie des fichiers essentiels..."

# Fichiers essentiels
ESSENTIAL_FILES=(
    "serveur_simple.py"
    "start.sh"
    "index.html"
    "dashboard_final_integration.html"
    "bulletin_lumen.html"
    "dashboard_pedagogique.html"
    "dashboard_simplifie.html"
    "requirements.txt"
    "README.md"
    "check_files.sh"
    "fix_missing_dashboards.sh"
    "generate_all_dashboards.py"
    "dashboard_integration.py"
    "cleanup_project.sh"
    "aggressive_cleanup.sh"
    ".gitignore"
)

# Copier les fichiers essentiels
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "✅ $file"
    else
        echo "⚠️  $file manquant"
    fi
done

# Copier les dossiers nécessaires (sans les gros fichiers)
if [ -d "data/processed" ]; then
    mkdir -p "$DEPLOY_DIR/data/processed"
    # Copier seulement les fichiers essentiels
    find data/processed -name "*.parquet" -size -50M -exec cp {} "$DEPLOY_DIR/data/processed/" \; 2>/dev/null || true
    find data/processed -name "*.csv" -size -10M -exec cp {} "$DEPLOY_DIR/data/processed/" \; 2>/dev/null || true
fi

if [ -d "models" ]; then
    mkdir -p "$DEPLOY_DIR/models"
    # Copier seulement les modèles essentiels
    find models -name "*.joblib" -size -50M -exec cp {} "$DEPLOY_DIR/models/" \; 2>/dev/null || true
fi

if [ -d "monitoring" ]; then
    cp -r monitoring "$DEPLOY_DIR/"
    # Supprimer les logs volumineux
    rm -rf "$DEPLOY_DIR/monitoring/logs" 2>/dev/null || true
fi

if [ -d "ml" ]; then
    cp -r ml "$DEPLOY_DIR/"
    # Supprimer les artefacts volumineux
    rm -rf "$DEPLOY_DIR/ml/artefacts" 2>/dev/null || true
fi

# Rendre les scripts exécutables
chmod +x "$DEPLOY_DIR"/*.sh

echo "✅ Déploiement propre créé dans : $DEPLOY_DIR"
echo ""
echo "📊 Taille du package :"
du -sh "$DEPLOY_DIR"

echo ""
echo "📋 Instructions pour la machine de destination :"
echo "1. Copiez le dossier '$DEPLOY_DIR' sur la machine cible"
echo "2. cd $DEPLOY_DIR"
echo "3. ./check_files.sh  # Vérifier les fichiers"
echo "4. ./start.sh        # Lancer le projet (génère automatiquement les dashboards manquants)"
echo ""
echo "🎯 Avantages du déploiement propre :"
echo "• Taille réduite (pas de données volumineuses)"
echo "• Dashboards générés automatiquement"
echo "• Nettoyage automatique des fichiers temporaires"
echo "• Démarrage rapide et fiable"
