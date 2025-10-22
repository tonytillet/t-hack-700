#!/bin/bash

# 🧪 Script de test de la configuration Docker

echo "🧪 Test de la configuration Docker LUMEN"
echo "========================================"

# Vérifier Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker installé : $(docker --version)"
else
    echo "❌ Docker non installé"
    echo "💡 Installez Docker depuis https://docker.com"
fi

# Vérifier Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose installé : $(docker-compose --version)"
else
    echo "❌ Docker Compose non installé"
    echo "💡 Installez Docker Compose depuis https://docs.docker.com/compose/install/"
fi

# Vérifier que Docker est démarré
if docker info &> /dev/null; then
    echo "✅ Docker daemon en cours d'exécution"
else
    echo "❌ Docker daemon non démarré"
    echo "💡 Démarrez Docker Desktop ou le service Docker"
fi

# Vérifier les fichiers Docker
echo ""
echo "📁 Vérification des fichiers Docker :"

DOCKER_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-entrypoint.sh"
    "docker-manage.sh"
)

for file in "${DOCKER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
    fi
done

# Vérifier les permissions
echo ""
echo "🔧 Vérification des permissions :"
if [ -x "docker-manage.sh" ]; then
    echo "✅ docker-manage.sh exécutable"
else
    echo "❌ docker-manage.sh non exécutable"
fi

if [ -x "docker-entrypoint.sh" ]; then
    echo "✅ docker-entrypoint.sh exécutable"
else
    echo "❌ docker-entrypoint.sh non exécutable"
fi

echo ""
echo "🎯 Pour utiliser Docker :"
echo "1. Démarrez Docker Desktop"
echo "2. ./docker-manage.sh build"
echo "3. ./docker-manage.sh start"
echo ""
echo "🚀 Pour déployer :"
echo "./deploy_docker.sh"
