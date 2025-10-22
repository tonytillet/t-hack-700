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
