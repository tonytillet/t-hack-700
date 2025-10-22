#!/bin/bash

# 🐳 Script de déploiement Docker pour LUMEN

echo "🐳 Déploiement Docker LUMEN"
echo "============================"

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    echo "💡 Installez Docker depuis https://docker.com"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    echo "💡 Installez Docker Compose depuis https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker et Docker Compose détectés"

# Créer un package de déploiement Docker
DEPLOY_DIR="lumen_docker_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

echo "📁 Création du package Docker..."

# Fichiers essentiels pour Docker
DOCKER_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-entrypoint.sh"
    "docker-manage.sh"
    "serveur_simple.py"
    "start.sh"
    "check_files.sh"
    "fix_missing_dashboards.sh"
    "generate_all_dashboards.py"
    "dashboard_integration.py"
    "requirements.txt"
    "README.md"
    ".gitignore"
)

# Copier les fichiers essentiels
for file in "${DOCKER_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "✅ $file"
    else
        echo "⚠️  $file manquant"
    fi
done

# Copier les dashboards HTML
cp *.html "$DEPLOY_DIR/" 2>/dev/null || true

# Copier les dossiers nécessaires (sans les gros fichiers)
if [ -d "data/processed" ]; then
    mkdir -p "$DEPLOY_DIR/data/processed"
    find data/processed -name "*.parquet" -size -50M -exec cp {} "$DEPLOY_DIR/data/processed/" \; 2>/dev/null || true
    find data/processed -name "*.csv" -size -10M -exec cp {} "$DEPLOY_DIR/data/processed/" \; 2>/dev/null || true
fi

if [ -d "models" ]; then
    mkdir -p "$DEPLOY_DIR/models"
    find models -name "*.joblib" -size -50M -exec cp {} "$DEPLOY_DIR/models/" \; 2>/dev/null || true
fi

if [ -d "monitoring" ]; then
    cp -r monitoring "$DEPLOY_DIR/"
    rm -rf "$DEPLOY_DIR/monitoring/logs" 2>/dev/null || true
fi

if [ -d "ml" ]; then
    cp -r ml "$DEPLOY_DIR/"
    rm -rf "$DEPLOY_DIR/ml/artefacts" 2>/dev/null || true
fi

# Rendre les scripts exécutables
chmod +x "$DEPLOY_DIR"/*.sh

# Créer un script de démarrage rapide
cat > "$DEPLOY_DIR/quick-start.sh" << 'EOF'
#!/bin/bash
echo "🚀 LUMEN - Démarrage Rapide Docker"
echo "=================================="
echo "1. Construction de l'image..."
./docker-manage.sh build
echo ""
echo "2. Démarrage du conteneur..."
./docker-manage.sh start
echo ""
echo "✅ LUMEN est maintenant accessible sur http://localhost:8080"
echo "🛑 Pour arrêter : ./docker-manage.sh stop"
EOF

chmod +x "$DEPLOY_DIR/quick-start.sh"

echo "✅ Package Docker créé dans : $DEPLOY_DIR"
echo ""
echo "📊 Taille du package :"
du -sh "$DEPLOY_DIR"

echo ""
echo "📋 Instructions pour la machine de destination :"
echo "1. Copiez le dossier '$DEPLOY_DIR' sur la machine cible"
echo "2. cd $DEPLOY_DIR"
echo "3. ./quick-start.sh  # Démarrage automatique"
echo "   OU"
echo "3. ./docker-manage.sh build  # Construction manuelle"
echo "4. ./docker-manage.sh start  # Démarrage manuel"
echo ""
echo "🎯 Avantages du déploiement Docker :"
echo "• Isolation complète (pas de conflits de ports)"
echo "• Environnement reproductible"
echo "• Gestion simplifiée des dépendances"
echo "• Démarrage/arrêt facile"
echo "• Pas de serveurs multiples"
echo ""
echo "🔧 Commandes de gestion :"
echo "• ./docker-manage.sh start    - Démarrer"
echo "• ./docker-manage.sh stop     - Arrêter"
echo "• ./docker-manage.sh restart  - Redémarrer"
echo "• ./docker-manage.sh logs     - Voir les logs"
echo "• ./docker-manage.sh status   - Voir le statut"
echo "• ./docker-manage.sh clean    - Nettoyer"
