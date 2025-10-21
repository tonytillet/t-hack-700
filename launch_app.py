#!/usr/bin/env python3
"""
Script pour lancer l'application Streamlit sans problème d'email
"""

import subprocess
import sys
import os

def launch_streamlit():
    """Lance Streamlit avec les bonnes options"""
    
    # Configuration pour éviter le prompt d'email
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Commande pour lancer Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 
        'main.py',
        '--server.port', '8501',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print("🚀 Lancement de l'application Streamlit...")
    print("📱 Ouvrez votre navigateur sur: http://localhost:8501")
    print("⏹️  Pour arrêter: Ctrl+C")
    print("-" * 50)
    
    try:
        # Lancement de Streamlit
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Application arrêtée")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    launch_streamlit()
