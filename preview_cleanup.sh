#!/bin/bash

# 👀 Aperçu du nettoyage - Montre ce qui sera supprimé

echo "👀 Aperçu du nettoyage LUMEN..."
echo "==============================="

echo "🗑️  Fichiers temporaires à supprimer :"
ls -la serveur_simple.py.tmp serveur_temp.py serveur_temp.py.tmp 2>/dev/null || echo "   (aucun fichier temporaire trouvé)"

echo ""
echo "📚 Documentation redondante à supprimer :"
for file in DEMARRAGE_COMPLET.md LANCEMENT_LOCAL.md SERVEUR_UNIQUE.md NETTOYAGE_GIT.md STRUCTURE_FINALE.md PIPELINE_DONNEES_COMPLET.md METRIQUES_PUBLIQUES.md SCRIPTS_GENERATION_DASHBOARDS.md GUIDE_DEPANNAGE_DASHBOARDS.md GUIDE_DEPLOIEMENT.md GUIDE_GENERATION_HTML.md; do
    if [ -f "$file" ]; then
        echo "   - $file ($(du -h "$file" | cut -f1))"
    fi
done

echo ""
echo "🔧 Scripts redondants à supprimer :"
for file in generate_dashboards.sh check_servers.sh clean_data_controlled.py validate_data_strict.py generate_meaningful_data.py monitoring_auto_retrain.py explicabilite_shap.py; do
    if [ -f "$file" ]; then
        echo "   - $file ($(du -h "$file" | cut -f1))"
    fi
done

echo ""
echo "🐳 Fichiers Docker inutiles à supprimer :"
for file in compose.dev.yml compose.yml Dockerfile Makefile; do
    if [ -f "$file" ]; then
        echo "   - $file ($(du -h "$file" | cut -f1))"
    fi
done

echo ""
echo "📊 Logs volumineux à nettoyer :"
if [ -d "data/logs" ]; then
    find data/logs -name "*.csv" -size +1M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
    find data/logs -name "*.json" -size +1M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
    find data/logs -name "*.txt" -size +1M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
fi

echo ""
echo "🤖 Artefacts ML volumineux à nettoyer :"
if [ -d "ml/artefacts" ]; then
    find ml/artefacts -name "*.joblib" -size +10M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
    find ml/artefacts -name "*.pkl" -size +10M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
fi

echo ""
echo "🧠 Modèles anciens à nettoyer :"
if [ -d "models" ]; then
    find models -name "*.joblib" -type f -printf '%T@ %p %s\n' | sort -n | head -n -1 | while read timestamp file size; do
        echo "   - $file ($(du -h "$file" | cut -f1))"
    done
fi

echo ""
echo "📈 Logs de monitoring anciens à nettoyer :"
if [ -d "monitoring/logs" ]; then
    find monitoring/logs -name "*.json" -mtime +7 -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
fi

echo ""
echo "🔍 Fichiers d'explicabilité volumineux à nettoyer :"
if [ -d "explicabilite/plots" ]; then
    find explicabilite/plots -name "*.png" -size +5M -exec echo "   - {} ($(du -h {} | cut -f1))" \; 2>/dev/null
fi

echo ""
echo "📊 Taille totale du projet avant nettoyage :"
du -sh . 2>/dev/null || echo "   (impossible de calculer)"

echo ""
echo "✅ Fichiers essentiels qui seront conservés :"
echo "   • serveur_simple.py"
echo "   • start.sh"
echo "   • index.html + dashboards"
echo "   • requirements.txt"
echo "   • README.md"
echo "   • Scripts de génération essentiels"

echo ""
echo "🚀 Pour exécuter le nettoyage : ./cleanup_project.sh"
