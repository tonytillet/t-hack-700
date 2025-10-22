#!/bin/bash

# 🚀 LUMEN - Script de Lancement Automatique

echo "🧠 LUMEN - Démarrage du Système"
echo "================================"

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

# Vérifier et réparer les dashboards manquants
echo "🔍 Vérification des dashboards..."
./check_files.sh

# Si des dashboards sont manquants, les réparer
if [ -f "fix_missing_dashboards.sh" ]; then
    echo "🔧 Réparation automatique des dashboards manquants..."
    ./fix_missing_dashboards.sh
fi

# Vérifier si les fichiers essentiels existent
if [ ! -f "serveur_simple.py" ]; then
    echo "❌ Fichier serveur_simple.py manquant"
    exit 1
fi

# Vérifier s'il y a déjà un serveur LUMEN en cours
if pgrep -f "serveur_simple.py\|serveur_temp.py" > /dev/null; then
    echo "⚠️  Un serveur LUMEN est déjà en cours d'exécution"
    echo "🛑 Arrêt du serveur existant..."
    pkill -f "serveur_simple.py\|serveur_temp.py"
    sleep 3
fi

# Vérifier à nouveau
if pgrep -f "serveur_simple.py\|serveur_temp.py" > /dev/null; then
    echo "❌ Impossible d'arrêter le serveur existant"
    echo "💡 Utilisez 'pkill -f python3' manuellement"
    exit 1
fi

# Trouver un port libre
PORT=8081
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "🚀 Lancement sur le port $PORT..."

# Créer une copie temporaire du serveur avec le bon port
cp serveur_simple.py serveur_temp.py
sed -i.tmp "s/PORT = [0-9]*/PORT = $PORT/" serveur_temp.py

# Lancer le serveur temporaire
echo "🚀 Lancement du serveur LUMEN..."
python3 serveur_temp.py &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 3

# Vérifier que le serveur est bien lancé
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Le serveur n'a pas pu démarrer"
    rm -f serveur_temp.py serveur_temp.py.tmp
    exit 1
fi

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
    
    # Fonction de nettoyage à l'arrêt
    cleanup() {
        echo ""
        echo "🛑 Arrêt du serveur LUMEN..."
        pkill -f "serveur_temp.py" 2>/dev/null || true
        sleep 1
        rm -f serveur_temp.py serveur_temp.py.tmp
        echo "✅ Serveur arrêté et fichiers temporaires supprimés"
        exit 0
    }
    
    # Capturer Ctrl+C
    trap cleanup SIGINT SIGTERM
    
    # Attendre que l'utilisateur arrête le serveur
    wait
else
    echo "❌ Erreur lors du lancement du serveur"
    echo "💡 Vérifiez que le port $PORT est libre"
    rm -f serveur_temp.py serveur_temp.py.tmp
    exit 1
fi