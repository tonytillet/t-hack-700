#!/usr/bin/env python3
"""
Script pour vérifier que l'application fonctionne
"""

import requests
import time

def check_app():
    """Vérifie que l'application répond"""
    url = "http://localhost:8501"
    
    print("🔍 Vérification de l'application...")
    
    for i in range(5):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Application accessible!")
                print(f"📱 Ouvrez votre navigateur sur: {url}")
                return True
            else:
                print(f"⏳ Tentative {i+1}/5 - Code: {response.status_code}")
        except Exception as e:
            print(f"⏳ Tentative {i+1}/5 - Erreur: {e}")
        
        time.sleep(2)
    
    print("❌ Application non accessible")
    return False

if __name__ == "__main__":
    check_app()
