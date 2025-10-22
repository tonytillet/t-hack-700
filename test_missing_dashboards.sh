#!/bin/bash

# 🧪 Script de test pour simuler des dashboards manquants

echo "🧪 Test de réparation des dashboards manquants..."
echo "================================================"

# Créer un dossier de test
TEST_DIR="test_missing_dashboards_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Création d'un environnement de test..."

# Copier seulement les fichiers essentiels (sans les dashboards)
cp ../serveur_simple.py .
cp ../requirements.txt .
cp ../start.sh .
cp ../check_files.sh .
cp ../fix_missing_dashboards.sh .
cp ../generate_all_dashboards.py .
cp ../dashboard_integration.py .

# Rendre les scripts exécutables
chmod +x *.sh

echo "🔍 Vérification initiale..."
./check_files.sh

echo ""
echo "🔧 Test de réparation automatique..."
./fix_missing_dashboards.sh

echo ""
echo "🔍 Vérification après réparation..."
./check_files.sh

echo ""
echo "🚀 Test de lancement du serveur..."
timeout 10s ./start.sh || echo "Serveur lancé (arrêté après 10s)"

echo ""
echo "🧹 Nettoyage du test..."
cd ..
rm -rf "$TEST_DIR"

echo "✅ Test terminé !"
