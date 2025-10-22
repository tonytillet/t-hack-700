#!/bin/bash
# LUMEN - Retrain hebdomadaire
# Exécuté chaque dimanche à 2h00

cd /Users/meriemzahzouh/epitech/t-hack-700/t-hack-700

echo "$(date): Début du retrain hebdomadaire LUMEN" >> monitoring/logs/weekly_retrain.log

# Exécuter le retrain complet
python3 monitoring_auto_retrain.py >> monitoring/logs/weekly_retrain.log 2>&1

# Générer un rapport de performance
python3 -c "
import json
from pathlib import Path
from datetime import datetime

# Lire les dernières métriques
logs_dir = Path('monitoring/logs')
metrics_files = list(logs_dir.glob('metrics_*.json'))
if metrics_files:
    latest_metrics = max(metrics_files, key=lambda x: x.stat().st_mtime)
    with open(latest_metrics) as f:
        metrics = json.load(f)
    
    print(f'📊 Rapport hebdomadaire LUMEN - {datetime.now().strftime(\"%d/%m/%Y\")}')
    print(f'R² Score: {metrics[\"r2_score\"]:.4f}')
    print(f'MAE: {metrics[\"mae\"]:.4f}')
    print(f'Modèle: {metrics[\"model_path\"]}')
" >> monitoring/logs/weekly_retrain.log

echo "$(date): Fin du retrain hebdomadaire LUMEN" >> monitoring/logs/weekly_retrain.log
