@echo off
REM 🚨 Script d'installation automatique - Système d'alerte grippe France
REM Usage: install.bat

echo 🚨 Installation du système d'alerte grippe France
echo ==================================================

REM Vérification de Python
echo 📋 Vérification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérification de pip
echo 📋 Vérification de pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)
echo ✅ pip détecté

REM Installation des dépendances
echo 📦 Installation des dépendances...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)
echo ✅ Dépendances installées

REM Création des dossiers nécessaires
echo 📁 Création des dossiers...
if not exist "data" mkdir data
if not exist "data\spf" mkdir data\spf
if not exist "data\insee" mkdir data\insee
if not exist "data\meteo" mkdir data\meteo
if not exist "data\wikipedia" mkdir data\wikipedia
if not exist "data\google_trends" mkdir data\google_trends
if not exist "data\processed" mkdir data\processed
if not exist "data\alerts" mkdir data\alerts
if not exist "models" mkdir models

REM Collecte des données
echo 📊 Collecte des données...
python scripts\collect_real_data_fixed.py
if %errorlevel% neq 0 (
    echo ⚠️  Erreur lors de la collecte des données, mais on continue...
)

REM Fusion des données
echo 🔄 Fusion des données...
python scripts\fuse_data.py
if %errorlevel% neq 0 (
    echo ⚠️  Erreur lors de la fusion des données, mais on continue...
)

REM Génération des alertes
echo 🚨 Génération des alertes...
python scripts\create_alert_system.py
if %errorlevel% neq 0 (
    echo ⚠️  Erreur lors de la génération des alertes, mais on continue...
)

echo.
echo 🎉 Installation terminée !
echo.
echo 🚀 Pour lancer l'application :
echo    python launch_app.py
echo.
echo 🌐 L'application sera accessible sur :
echo    http://localhost:8501
echo.
echo 📚 Pour plus d'informations, consultez le README.md
pause
