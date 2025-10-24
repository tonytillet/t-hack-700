#!/bin/bash
echo "🧠 LUMEN - Démarrage Ultra-Rapide"
echo "=================================="
echo "Construction et lancement en cours..."
docker run -d -p 8501:8501 --name lumen $(docker build -q .)
echo " LUMEN démarré sur http://localhost:8501"
echo " Pour arrêter: docker stop lumen && docker rm lumen"
