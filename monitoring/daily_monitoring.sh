#!/bin/bash
# LUMEN - Monitoring quotidien
# Exécuté chaque jour à 6h00

cd /Users/meriemzahzouh/epitech/t-hack-700/t-hack-700
python3 monitoring_auto_retrain.py >> monitoring/logs/daily_monitoring.log 2>&1

# Nettoyer les logs anciens (garder 30 jours)
find monitoring/logs -name "*.log" -mtime +30 -delete
find monitoring/logs -name "*.json" -mtime +30 -delete
