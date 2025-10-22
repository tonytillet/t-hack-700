#!/bin/bash

# 🚀 LUMEN Enhanced - Script de Lancement Automatique

echo "🧠 LUMEN Enhanced - Démarrage du Système"
echo "========================================"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "💡 Installez Python 3.7+ depuis https://python.org"
    exit 1
fi

# Vérifier si les dépendances sont installées
if [ ! -f "requirements.txt" ]; then
    echo "❌ Fichier requirements.txt manquant"
    exit 1
fi

echo "📦 Vérification des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1

# Vérifier si les fichiers essentiels existent
if [ ! -f "serveur_simple.py" ]; then
    echo "❌ Fichier serveur_simple.py manquant"
    exit 1
fi

# Arrêter les processus Python existants
echo "🛑 Arrêt des processus existants..."
pkill -f python3 2>/dev/null || true

# Attendre un peu
sleep 2

# Trouver un port libre
PORT=8080
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "🚀 Lancement sur le port $PORT..."

# Modifier temporairement le port dans le fichier
sed -i.bak "s/PORT = [0-9]*/PORT = $PORT/" serveur_simple.py

# Lancer le serveur
python3 serveur_simple.py &

# Attendre que le serveur démarre
sleep 3

# Vérifier que le serveur fonctionne
if curl -s http://localhost:$PORT/ > /dev/null; then
    echo ""
    echo "✅ Serveur LUMEN lancé avec succès !"
    echo "🌐 Accédez au projet : http://localhost:$PORT/"
    echo ""
    echo "📊 Dashboards disponibles :"
    echo "   • Menu Principal    : http://localhost:$PORT/"
    echo "   • Bulletin Public   : http://localhost:$PORT/bulletin_lumen.html"
    echo "   • Vue Pédagogique   : http://localhost:$PORT/dashboard_pedagogique.html"
    echo "   • Carte des Risques : http://localhost:$PORT/dashboard_risk_heatmap.html"
    echo "   • Prédictions       : http://localhost:$PORT/dashboard_real_vs_predicted.html"
    echo "   • Alertes Actives   : http://localhost:$PORT/dashboard_active_alerts.html"
    echo ""
    echo "🛑 Pour arrêter : Ctrl+C ou 'pkill -f python3'"
    echo ""
    
    # Ouvrir automatiquement le navigateur (optionnel)
    if command -v open &> /dev/null; then
        echo "🌐 Ouverture automatique du navigateur..."
        open http://localhost:$PORT/
    elif command -v xdg-open &> /dev/null; then
        echo "🌐 Ouverture automatique du navigateur..."
        xdg-open http://localhost:$PORT/
    fi
    
    # Attendre que l'utilisateur arrête le serveur
    wait
else
    echo "❌ Erreur lors du lancement du serveur"
    echo "💡 Vérifiez que le port $PORT est libre"
    exit 1
fi
