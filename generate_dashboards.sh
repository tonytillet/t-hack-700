#!/bin/bash

# 🎨 Script de génération des dashboards LUMEN

echo "🎨 Génération des dashboards LUMEN..."
echo "===================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que le script d'intégration existe
if [ ! -f "dashboard_integration.py" ]; then
    echo "❌ Script dashboard_integration.py manquant"
    exit 1
fi

echo "📊 Génération des visualisations..."

# Exécuter le script d'intégration
python3 dashboard_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dashboards générés avec succès !"
    echo ""
    echo "📁 Fichiers créés :"
    echo "   • dashboard_risk_heatmap.html - Carte des zones à risque"
    echo "   • dashboard_real_vs_predicted.html - Graphiques réel vs prédit"
    echo "   • dashboard_active_alerts.html - Panneau des alertes actives"
    echo ""
    echo "🌐 Les dashboards sont maintenant disponibles via le serveur web"
else
    echo "❌ Erreur lors de la génération des dashboards"
    exit 1
fi
