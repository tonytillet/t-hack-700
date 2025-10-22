#!/bin/bash

# 🔧 Script de réparation des dashboards manquants

echo "🔧 Réparation des dashboards LUMEN manquants..."
echo "=============================================="

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "💡 Installez Python 3.7+ depuis https://python.org"
    exit 1
fi

# Liste des dashboards requis
REQUIRED_DASHBOARDS=(
    "index.html"
    "dashboard_final_integration.html"
    "bulletin_lumen.html"
    "dashboard_pedagogique.html"
    "dashboard_simplifie.html"
    "dashboard_risk_heatmap.html"
    "dashboard_real_vs_predicted.html"
    "dashboard_active_alerts.html"
)

echo "🔍 Vérification des dashboards requis..."

missing_dashboards=()
for dashboard in "${REQUIRED_DASHBOARDS[@]}"; do
    if [ -f "$dashboard" ]; then
        echo "✅ $dashboard"
    else
        echo "❌ $dashboard - MANQUANT"
        missing_dashboards+=("$dashboard")
    fi
done

if [ ${#missing_dashboards[@]} -eq 0 ]; then
    echo ""
    echo "✅ Tous les dashboards sont présents !"
    echo "🚀 Vous pouvez lancer le projet avec : ./start.sh"
    exit 0
fi

echo ""
echo "🔧 Réparation des dashboards manquants..."

# 1. Générer tous les dashboards
if [ -f "generate_all_dashboards.py" ]; then
    echo "🎨 Génération complète des dashboards..."
    python3 generate_all_dashboards.py
elif [ -f "dashboard_integration.py" ]; then
    echo "🎨 Génération des dashboards dynamiques..."
    python3 dashboard_integration.py
else
    echo "❌ Aucun script de génération trouvé"
    exit 1
fi

# 2. Vérifier à nouveau
echo ""
echo "🔍 Vérification après réparation..."

still_missing=()
for dashboard in "${missing_dashboards[@]}"; do
    if [ -f "$dashboard" ]; then
        echo "✅ $dashboard - RÉPARÉ"
    else
        echo "❌ $dashboard - TOUJOURS MANQUANT"
        still_missing+=("$dashboard")
    fi
done

# 3. Créer les dashboards manquants avec des templates de base
if [ ${#still_missing[@]} -gt 0 ]; then
    echo ""
    echo "🛠️  Création des templates de base pour les dashboards manquants..."
    
    for dashboard in "${still_missing[@]}"; do
        echo "📝 Création de $dashboard..."
        create_basic_dashboard "$dashboard"
    done
fi

# 4. Vérification finale
echo ""
echo "🎉 RÉPARATION TERMINÉE"
echo "====================="

final_missing=()
for dashboard in "${REQUIRED_DASHBOARDS[@]}"; do
    if [ -f "$dashboard" ]; then
        echo "✅ $dashboard"
    else
        echo "❌ $dashboard - TOUJOURS MANQUANT"
        final_missing+=("$dashboard")
    fi
done

if [ ${#final_missing[@]} -eq 0 ]; then
    echo ""
    echo "✅ Tous les dashboards sont maintenant présents !"
    echo "🚀 Vous pouvez lancer le projet avec : ./start.sh"
else
    echo ""
    echo "⚠️  ${#final_missing[@]} dashboards toujours manquants :"
    for dashboard in "${final_missing[@]}"; do
        echo "   - $dashboard"
    done
    echo ""
    echo "💡 Vérifiez que tous les fichiers ont été copiés correctement"
fi

# Fonction pour créer un dashboard de base
create_basic_dashboard() {
    local dashboard_name="$1"
    local title="LUMEN Dashboard"
    local icon="fas fa-chart-bar"
    
    case "$dashboard_name" in
        "index.html")
            title="LUMEN - Menu Principal"
            icon="fas fa-brain"
            ;;
        "dashboard_final_integration.html")
            title="LUMEN - Dashboard Principal"
            icon="fas fa-chart-line"
            ;;
        "bulletin_lumen.html")
            title="Bulletin LUMEN"
            icon="fas fa-bell"
            ;;
        "dashboard_pedagogique.html")
            title="LUMEN - Vue Pédagogique"
            icon="fas fa-graduation-cap"
            ;;
        "dashboard_simplifie.html")
            title="LUMEN - Vue Simplifiée"
            icon="fas fa-eye"
            ;;
        "dashboard_risk_heatmap.html")
            title="LUMEN - Carte des Zones à Risque"
            icon="fas fa-map-marked-alt"
            ;;
        "dashboard_real_vs_predicted.html")
            title="LUMEN - Prédictions vs Réalité"
            icon="fas fa-chart-area"
            ;;
        "dashboard_active_alerts.html")
            title="LUMEN - Alertes Actives"
            icon="fas fa-exclamation-triangle"
            ;;
    esac
    
    cat > "$dashboard_name" << EOF
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .content { background: white; border-radius: 10px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .status { color: #27ae60; font-size: 1.2rem; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="$icon"></i> $title</h1>
            <p>Surveillance épidémiologique intelligente</p>
        </div>
        
        <div class="content">
            <i class="$icon" style="font-size: 4rem; color: #3498db; margin-bottom: 20px;"></i>
            <h3>Dashboard LUMEN</h3>
            <p class="status">✅ Dashboard opérationnel</p>
            <p>Ce dashboard sera mis à jour automatiquement par le système LUMEN</p>
            <p><strong>Dernière mise à jour:</strong> $(date '+%d/%m/%Y %H:%M:%S')</p>
        </div>
    </div>
</body>
</html>
EOF
    
    echo "✅ Template de base créé pour $dashboard_name"
}
