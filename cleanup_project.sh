#!/bin/bash

# 🧹 Script de nettoyage complet du projet LUMEN

echo "🧹 Nettoyage complet du projet LUMEN..."
echo "======================================="

# Arrêter tous les processus
echo "🛑 Arrêt des processus..."
pkill -f python3 2>/dev/null || true
sleep 2

# Fichiers temporaires à supprimer
echo "🗑️  Suppression des fichiers temporaires..."

# Fichiers serveur temporaires
rm -f serveur_simple.py.tmp
rm -f serveur_temp.py
rm -f serveur_temp.py.tmp

# Fichiers de test
rm -f test_missing_dashboards.sh

# Fichiers de documentation redondants
rm -f DEMARRAGE_COMPLET.md
rm -f LANCEMENT_LOCAL.md
rm -f SERVEUR_UNIQUE.md
rm -f NETTOYAGE_GIT.md
rm -f STRUCTURE_FINALE.md
rm -f PIPELINE_DONNEES_COMPLET.md
rm -f METRIQUES_PUBLIQUES.md
rm -f SCRIPTS_GENERATION_DASHBOARDS.md
rm -f GUIDE_DEPANNAGE_DASHBOARDS.md
rm -f GUIDE_DEPLOIEMENT.md
rm -f GUIDE_GENERATION_HTML.md

# Scripts redondants
rm -f generate_dashboards.sh
rm -f check_servers.sh
rm -f clean_data_controlled.py
rm -f validate_data_strict.py
rm -f generate_meaningful_data.py
rm -f monitoring_auto_retrain.py
rm -f explicabilite_shap.py

# Fichiers Docker inutiles
rm -f compose.dev.yml
rm -f compose.yml
rm -f Dockerfile
rm -f Makefile

# Fichiers de navigation redondants
rm -f navigation.html

# Nettoyer les logs volumineux
echo "📊 Nettoyage des logs volumineux..."
if [ -d "data/logs" ]; then
    find data/logs -name "*.csv" -size +1M -delete 2>/dev/null || true
    find data/logs -name "*.json" -size +1M -delete 2>/dev/null || true
    find data/logs -name "*.txt" -size +1M -delete 2>/dev/null || true
fi

# Nettoyer les artefacts ML volumineux
echo "🤖 Nettoyage des artefacts ML..."
if [ -d "ml/artefacts" ]; then
    find ml/artefacts -name "*.joblib" -size +10M -delete 2>/dev/null || true
    find ml/artefacts -name "*.pkl" -size +10M -delete 2>/dev/null || true
fi

# Nettoyer les modèles anciens
echo "🧠 Nettoyage des modèles anciens..."
if [ -d "models" ]; then
    # Garder seulement le modèle le plus récent
    find models -name "*.joblib" -type f -printf '%T@ %p\n' | sort -n | head -n -1 | cut -d' ' -f2- | xargs rm -f 2>/dev/null || true
fi

# Nettoyer les fichiers de monitoring anciens
echo "📈 Nettoyage des logs de monitoring..."
if [ -d "monitoring/logs" ]; then
    find monitoring/logs -name "*.json" -mtime +7 -delete 2>/dev/null || true
fi

# Nettoyer les fichiers d'explicabilité volumineux
echo "🔍 Nettoyage des fichiers d'explicabilité..."
if [ -d "explicabilite/plots" ]; then
    find explicabilite/plots -name "*.png" -size +5M -delete 2>/dev/null || true
fi

# Créer un fichier .gitignore propre
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
ml/artefacts/*.joblib
ml/artefacts/*.pkl
ml/artefacts/*.png

# Logs et monitoring
monitoring/logs/
evidence/

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
EOF

echo "✅ Nettoyage terminé !"
echo ""
echo "📊 Résumé du nettoyage :"
echo "• Fichiers temporaires supprimés"
echo "• Documentation redondante supprimée"
echo "• Scripts inutiles supprimés"
echo "• Logs volumineux nettoyés"
echo "• Modèles anciens supprimés"
echo "• .gitignore mis à jour"
echo ""
echo "🎯 Fichiers essentiels conservés :"
echo "• serveur_simple.py"
echo "• start.sh"
echo "• index.html + dashboards"
echo "• requirements.txt"
echo "• README.md"
echo "• Scripts de génération"
echo ""
echo "🚀 Le projet est maintenant propre et optimisé !"
