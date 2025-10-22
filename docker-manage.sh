#!/bin/bash

# 🐳 Script de gestion Docker pour LUMEN

echo "🐳 LUMEN - Gestion Docker"
echo "========================="

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     - Construire l'image Docker"
    echo "  start     - Démarrer le conteneur"
    echo "  stop      - Arrêter le conteneur"
    echo "  restart   - Redémarrer le conteneur"
    echo "  logs      - Afficher les logs"
    echo "  status    - Afficher le statut"
    echo "  clean     - Nettoyer les conteneurs et images"
    echo "  shell     - Ouvrir un shell dans le conteneur"
    echo "  help      - Afficher cette aide"
}

# Fonction de construction
build_image() {
    echo "🔨 Construction de l'image Docker LUMEN..."
    docker build -t lumen-app .
    if [ $? -eq 0 ]; then
        echo "✅ Image construite avec succès"
    else
        echo "❌ Erreur lors de la construction"
        exit 1
    fi
}

# Fonction de démarrage
start_container() {
    echo "🚀 Démarrage du conteneur LUMEN..."
    
    # Arrêter les conteneurs existants
    docker-compose down 2>/dev/null || true
    
    # Démarrer le conteneur
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Conteneur démarré avec succès"
        echo "🌐 LUMEN accessible sur : http://localhost:8080"
        echo "📊 Dashboards disponibles :"
        echo "   • Menu Principal    : http://localhost:8080/"
        echo "   • Bulletin Public   : http://localhost:8080/bulletin_lumen.html"
        echo "   • Vue Pédagogique   : http://localhost:8080/dashboard_pedagogique.html"
        echo "   • Carte des Risques : http://localhost:8080/dashboard_risk_heatmap.html"
        echo "   • Prédictions       : http://localhost:8080/dashboard_real_vs_predicted.html"
        echo "   • Alertes Actives   : http://localhost:8080/dashboard_active_alerts.html"
    else
        echo "❌ Erreur lors du démarrage"
        exit 1
    fi
}

# Fonction d'arrêt
stop_container() {
    echo "🛑 Arrêt du conteneur LUMEN..."
    docker-compose down
    echo "✅ Conteneur arrêté"
}

# Fonction de redémarrage
restart_container() {
    echo "🔄 Redémarrage du conteneur LUMEN..."
    stop_container
    start_container
}

# Fonction de logs
show_logs() {
    echo "📋 Logs du conteneur LUMEN..."
    docker-compose logs -f
}

# Fonction de statut
show_status() {
    echo "📊 Statut du conteneur LUMEN..."
    docker-compose ps
    echo ""
    echo "🔍 Santé du conteneur :"
    docker inspect lumen-app --format='{{.State.Health.Status}}' 2>/dev/null || echo "Non disponible"
}

# Fonction de nettoyage
clean_docker() {
    echo "🧹 Nettoyage Docker..."
    
    # Arrêter et supprimer les conteneurs
    docker-compose down --volumes --remove-orphans
    
    # Supprimer l'image
    docker rmi lumen-app 2>/dev/null || true
    
    # Nettoyer les images inutilisées
    docker image prune -f
    
    echo "✅ Nettoyage terminé"
}

# Fonction de shell
open_shell() {
    echo "🐚 Ouverture d'un shell dans le conteneur..."
    docker exec -it lumen-app /bin/bash
}

# Gestion des arguments
case "${1:-help}" in
    build)
        build_image
        ;;
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_docker
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac
