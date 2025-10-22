#!/bin/bash

# 🧹 Nettoyage agressif du projet LUMEN

echo "🧹 Nettoyage agressif du projet LUMEN..."
echo "======================================="

# Arrêter tous les processus
echo "🛑 Arrêt des processus..."
pkill -f python3 2>/dev/null || true
sleep 2

# Supprimer complètement les dossiers volumineux
echo "🗑️  Suppression des dossiers volumineux..."

# Supprimer les données brutes (garder seulement les données essentielles)
if [ -d "data/raw" ]; then
    echo "   Suppression de data/raw/ ($(du -sh data/raw | cut -f1))"
    rm -rf data/raw
fi

if [ -d "data/cleaned" ]; then
    echo "   Suppression de data/cleaned/ ($(du -sh data/cleaned | cut -f1))"
    rm -rf data/cleaned
fi

if [ -d "data/frozen" ]; then
    echo "   Suppression de data/frozen/ ($(du -sh data/frozen | cut -f1))"
    rm -rf data/frozen
fi

if [ -d "data/logs" ]; then
    echo "   Suppression de data/logs/ ($(du -sh data/logs | cut -f1))"
    rm -rf data/logs
fi

# Supprimer les fichiers de données volumineux
if [ -d "data/processed" ]; then
    echo "   Nettoyage de data/processed/"
    find data/processed -name "*.parquet" -size +100M -delete 2>/dev/null || true
    find data/processed -name "*.csv" -size +100M -delete 2>/dev/null || true
fi

# Supprimer les artefacts ML volumineux
if [ -d "ml/artefacts" ]; then
    echo "   Suppression de ml/artefacts/ ($(du -sh ml/artefacts | cut -f1))"
    rm -rf ml/artefacts
fi

# Supprimer les modèles anciens
if [ -d "models" ]; then
    echo "   Nettoyage de models/"
    find models -name "*.joblib" -size +50M -delete 2>/dev/null || true
    find models -name "*.pkl" -size +50M -delete 2>/dev/null || true
fi

# Supprimer les fichiers d'explicabilité volumineux
if [ -d "explicabilite" ]; then
    echo "   Suppression de explicabilite/ ($(du -sh explicabilite | cut -f1))"
    rm -rf explicabilite
fi

# Supprimer les fichiers d'évidence
if [ -d "evidence" ]; then
    echo "   Suppression de evidence/ ($(du -sh evidence | cut -f1))"
    rm -rf evidence
fi

# Supprimer les logs de monitoring
if [ -d "monitoring/logs" ]; then
    echo "   Suppression de monitoring/logs/ ($(du -sh monitoring/logs | cut -f1))"
    rm -rf monitoring/logs
fi

# Supprimer les dashboards HTML volumineux (ils seront régénérés)
echo "🗑️  Suppression des dashboards HTML volumineux..."
rm -f dashboard_risk_heatmap.html
rm -f dashboard_real_vs_predicted.html

# Créer un .gitignore plus strict
echo "📝 Mise à jour du .gitignore..."
cat > .gitignore << 'EOF'
# Données volumineuses
data/raw/
data/cleaned/
data/frozen/
data/logs/
data/processed/*.parquet
data/processed/*.csv

# Modèles ML
models/*.joblib
models/*.pkl
models/*.csv
models/*.json

# Artefacts ML
ml/artefacts/
explicabilite/
evidence/

# Logs et monitoring
monitoring/logs/

# Fichiers temporaires
*.tmp
*.bak
*.log
__pycache__/
*.pyc
*.pyo

# Fichiers système
.DS_Store
Thumbs.db
.vscode/
.idea/

# Environnements virtuels
venv/
env/
.venv/

# Fichiers de déploiement
lumen_deploy_*/

# Dashboards générés (seront recréés automatiquement)
dashboard_risk_heatmap.html
dashboard_real_vs_predicted.html
dashboard_active_alerts.html
EOF

echo "✅ Nettoyage agressif terminé !"
echo ""
echo "📊 Taille du projet après nettoyage :"
du -sh . 2>/dev/null || echo "   (impossible de calculer)"

echo ""
echo "🎯 Fichiers essentiels conservés :"
echo "• serveur_simple.py"
echo "• start.sh"
echo "• index.html + dashboards principaux"
echo "• requirements.txt"
echo "• README.md"
echo "• Scripts de génération"

echo ""
echo "🔄 Les dashboards manquants seront régénérés automatiquement au prochain démarrage"
echo "🚀 Le projet est maintenant ultra-optimisé !"
