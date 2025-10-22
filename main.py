#!/usr/bin/env python3
"""
Application LUMEN - Point d'entrée principal
"""

import sys
import os

# Ajouter le répertoire src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import et lancement de l'application
from views.main_app import main

if __name__ == "__main__":
    main()
