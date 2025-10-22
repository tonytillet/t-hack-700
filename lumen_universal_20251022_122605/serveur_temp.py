#!/usr/bin/env python3
"""
🌐 LUMEN - Serveur Simple Unifié
Un seul port pour tout
"""

import http.server
import socketserver
import os
from pathlib import Path

class LUMENHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Redirection vers le menu principal
        if self.path == '/':
            self.path = '/index.html'
        
        # Servir le fichier
        return super().do_GET()

def main():
    PORT = 8086
    
    print("🌐 LUMEN - SERVEUR UNIFIÉ")
    print("=" * 40)
    print(f"🚀 Port unique: {PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/")
    print(f"🗺️ Carte: http://localhost:{PORT}/dashboard_risk_heatmap.html")
    print(f"📈 Prédictions: http://localhost:{PORT}/dashboard_real_vs_predicted.html")
    print(f"🚨 Alertes: http://localhost:{PORT}/dashboard_active_alerts.html")
    print(f"🔔 Bulletin: http://localhost:{PORT}/bulletin_lumen.html")
    print(f"📚 Pédagogique: http://localhost:{PORT}/dashboard_pedagogique.html")
    print("=" * 40)
    
    # Vérifier les fichiers
    if not Path('dashboard_final_integration.html').exists():
        print("❌ Fichier dashboard_final_integration.html manquant")
        print("💡 Exécutez: python3 dashboard_integration.py")
        return
    
    print("✅ Dashboard prêt")
    print(f"🌐 Serveur: http://localhost:{PORT}")
    print("🛑 Ctrl+C pour arrêter")
    
    try:
        with socketserver.TCPServer(("", PORT), LUMENHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} déjà utilisé")
            print("💡 Arrêtez avec: pkill -f python3")
        else:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
