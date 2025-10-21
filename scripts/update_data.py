#!/usr/bin/env python3
"""
Script de mise à jour automatique des données
Exécute la collecte et l'analyse des données
"""

import subprocess
import sys
import os
from datetime import datetime

def update_data():
    """Mettre à jour toutes les données"""
    print("🔄 MISE À JOUR DES DONNÉES LUMEN")
    print("=" * 50)
    print(f"⏰ Début: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # 1. Collecter les nouvelles données
        print("\n📊 Étape 1: Collecte des données...")
        result = subprocess.run([
            sys.executable, "scripts/collect_real_data_fixed.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de la collecte: {result.stderr}")
            return False
        
        print("✅ Collecte terminée")
        
        # 2. Créer le système d'alerte
        print("\n🚨 Étape 2: Analyse des alertes...")
        result = subprocess.run([
            sys.executable, "scripts/create_alert_system.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'analyse: {result.stderr}")
            return False
        
        print("✅ Analyse terminée")
        
        print(f"\n🎉 MISE À JOUR TERMINÉE")
        print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = update_data()
    sys.exit(0 if success else 1)
