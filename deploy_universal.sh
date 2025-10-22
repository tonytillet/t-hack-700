#!/bin/bash

# 🚀 Script de déploiement universel LUMEN (Docker + Local)

echo "🚀 LUMEN - Déploiement Universel"
echo "================================="

# Détecter l'environnement
if docker info &> /dev/null; then
    echo "🐳 Docker détecté et disponible"
    DEPLOY_MODE="docker"
else
    echo "💻 Mode local détecté (Docker non disponible)"
    DEPLOY_MODE="local"
fi

# Créer un package de déploiement
DEPLOY_DIR="lumen_universal_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

echo "📁 Création du package universel..."

# Fichiers essentiels
ESSENTIAL_FILES=(
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
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "✅ $file"
    else
        echo "⚠️  $file manquant"
    fi
done

# Copier les dashboards HTML
cp *.html "$DEPLOY_DIR/" 2>/dev/null || true

# Copier les dossiers nécessaires
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

# Si Docker est disponible, copier les fichiers Docker
if [ "$DEPLOY_MODE" = "docker" ]; then
    echo "🐳 Ajout des fichiers Docker..."
    DOCKER_FILES=(
        "Dockerfile"
        "docker-compose.yml"
        "docker-entrypoint.sh"
        "docker-manage.sh"
    )
    
    for file in "${DOCKER_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$DEPLOY_DIR/"
            echo "✅ $file"
        fi
    done
fi

# Rendre les scripts exécutables
chmod +x "$DEPLOY_DIR"/*.sh

# Créer le script de démarrage adaptatif
cat > "$DEPLOY_DIR/start-lumen.sh" << 'EOF'
#!/bin/bash

echo "🚀 LUMEN - Démarrage Adaptatif"
echo "==============================="

# Détecter l'environnement
if docker info &> /dev/null; then
    echo "🐳 Docker détecté - Démarrage en mode Docker"
    echo ""
    echo "1. Construction de l'image..."
    ./docker-manage.sh build
    echo ""
    echo "2. Démarrage du conteneur..."
    ./docker-manage.sh start
    echo ""
    echo "✅ LUMEN Docker démarré sur http://localhost:8080"
    echo "🛑 Pour arrêter : ./docker-manage.sh stop"
else
    echo "💻 Docker non disponible - Démarrage en mode local"
    echo ""
    echo "🔧 Réparation des dashboards manquants..."
    ./fix_missing_dashboards.sh
    echo ""
    echo "🚀 Démarrage du serveur local..."
    ./start.sh
fi
EOF

chmod +x "$DEPLOY_DIR/start-lumen.sh"

# Créer un README adaptatif
cat > "$DEPLOY_DIR/README-DEPLOYMENT.md" << EOF
# 🚀 LUMEN - Guide de Déploiement

## 🎯 Démarrage Rapide

\`\`\`bash
./start-lumen.sh
\`\`\`

## 🐳 Mode Docker (Recommandé)

Si Docker est disponible :

\`\`\`bash
# Démarrage automatique
./start-lumen.sh

# Ou manuellement
./docker-manage.sh build
./docker-manage.sh start
\`\`\`

**Avantages Docker :**
- ✅ Isolation complète
- ✅ Pas de conflits de ports
- ✅ Environnement reproductible
- ✅ Gestion simplifiée

## 💻 Mode Local

Si Docker n'est pas disponible :

\`\`\`bash
# Démarrage automatique
./start-lumen.sh

# Ou manuellement
./fix_missing_dashboards.sh
./start.sh
\`\`\`

**Avantages Local :**
- ✅ Pas de Docker requis
- ✅ Démarrage rapide
- ✅ Débogage facile

## 🌐 Accès aux Dashboards

Une fois démarré, LUMEN est accessible sur :

- **Menu Principal :** http://localhost:8080/ (Docker) ou http://localhost:8081/ (Local)
- **Bulletin Public :** /bulletin_lumen.html
- **Vue Pédagogique :** /dashboard_pedagogique.html
- **Carte des Risques :** /dashboard_risk_heatmap.html
- **Prédictions :** /dashboard_real_vs_predicted.html
- **Alertes Actives :** /dashboard_active_alerts.html

## 🔧 Commandes de Gestion

### Docker :
\`\`\`bash
./docker-manage.sh start    # Démarrer
./docker-manage.sh stop     # Arrêter
./docker-manage.sh restart  # Redémarrer
./docker-manage.sh logs     # Voir les logs
./docker-manage.sh status   # Voir le statut
\`\`\`

### Local :
\`\`\`bash
./start.sh                  # Démarrer
pkill -f python3           # Arrêter
./fix_missing_dashboards.sh # Réparer
\`\`\`

## 🎉 Résultat

**LUMEN fonctionne parfaitement dans les deux modes !** 🚀
EOF

echo "✅ Package universel créé dans : $DEPLOY_DIR"
echo ""
echo "📊 Taille du package :"
du -sh "$DEPLOY_DIR"

echo ""
echo "📋 Instructions pour la machine de destination :"
echo "1. Copiez le dossier '$DEPLOY_DIR' sur la machine cible"
echo "2. cd $DEPLOY_DIR"
echo "3. ./start-lumen.sh  # Démarrage automatique adaptatif"
echo ""
echo "🎯 Le script détecte automatiquement :"
echo "• Si Docker est disponible → Mode Docker (recommandé)"
echo "• Si Docker n'est pas disponible → Mode Local"
echo ""
echo "🚀 LUMEN s'adapte à votre environnement !"
