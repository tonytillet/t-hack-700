#!/bin/bash

# 🔍 Script de vérification des fichiers LUMEN

echo "🔍 Vérification des fichiers LUMEN..."
echo "====================================="

# Fichiers essentiels
ESSENTIAL_FILES=(
    "serveur_simple.py"
    "index.html"
    "dashboard_final_integration.html"
    "bulletin_lumen.html"
    "dashboard_pedagogique.html"
    "dashboard_simplifie.html"
    "dashboard_risk_heatmap.html"
    "dashboard_real_vs_predicted.html"
    "dashboard_active_alerts.html"
    "requirements.txt"
)

# Fichiers optionnels
OPTIONAL_FILES=(
    "clean.sh"
    "start.sh"
    "README.md"
    "LANCEMENT_PROJET.md"
)

echo "📋 Vérification des fichiers essentiels..."
missing_essential=0
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MANQUANT"
        missing_essential=1
    fi
done

echo ""
echo "📋 Vérification des fichiers optionnels..."
for file in "${OPTIONAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "⚠️  $file - Optionnel"
    fi
done

echo ""
if [ $missing_essential -eq 0 ]; then
    echo "✅ Tous les fichiers essentiels sont présents !"
    echo "🚀 Vous pouvez lancer le projet avec : ./start.sh"
else
    echo "❌ Des fichiers essentiels sont manquants !"
    echo "💡 Vérifiez que tous les fichiers ont été copiés correctement"
    exit 1
fi

echo ""
echo "🔧 Vérification des permissions..."
if [ -x "start.sh" ]; then
    echo "✅ start.sh est exécutable"
else
    echo "⚠️  start.sh n'est pas exécutable - Correction..."
    chmod +x start.sh
fi

if [ -x "clean.sh" ]; then
    echo "✅ clean.sh est exécutable"
else
    echo "⚠️  clean.sh n'est pas exécutable - Correction..."
    chmod +x clean.sh
fi

echo ""
echo "🎉 Vérification terminée !"
