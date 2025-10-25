#!/usr/bin/env python3
"""
Script principal pour exécuter tout le pipeline ML
"""

import subprocess
import sys
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLPipeline:
    def __init__(self):
        self.scripts_dir = Path("scripts")
        self.pipeline_steps = [
            ("fit_stats.py", "Calcul des statistiques de référence"),
            ("make_features.py", "Création des features"),
            ("train_random_forest.py", "Entraînement du modèle"),
            ("predict.py", "Génération des prédictions")
        ]
    
    def run_script(self, script_name, description):
        """Exécute un script du pipeline"""
        logger.info(f"🚀 {description}")
        logger.info("=" * 60)
        
        try:
            script_path = self.scripts_dir / script_name
            if not script_path.exists():
                logger.error(f"❌ Script non trouvé: {script_path}")
                return False
            
            # Exécuter le script
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                logger.info(f"✅ {description} - SUCCÈS")
                if result.stdout:
                    logger.info(f"📊 Sortie: {result.stdout[-500:]}")  # Dernières 500 caractères
                return True
            else:
                logger.error(f"❌ {description} - ÉCHEC")
                logger.error(f"Erreur: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur exécution {script_name}: {e}")
            return False
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet"""
        logger.info("🚀 DÉBUT DU PIPELINE ML COMPLET")
        logger.info("=" * 80)
        logger.info(f"⏰ Heure de début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        success_count = 0
        total_steps = len(self.pipeline_steps)
        
        for i, (script_name, description) in enumerate(self.pipeline_steps, 1):
            logger.info(f"📋 ÉTAPE {i}/{total_steps}: {description}")
            logger.info("-" * 60)
            
            success = self.run_script(script_name, description)
            
            if success:
                success_count += 1
                logger.info(f"✅ Étape {i} terminée avec succès")
            else:
                logger.error(f"❌ Étape {i} échouée - Arrêt du pipeline")
                break
            
            logger.info("")
        
        # Résumé final
        logger.info("=" * 80)
        logger.info(f"📊 RÉSUMÉ DU PIPELINE")
        logger.info(f"✅ Étapes réussies: {success_count}/{total_steps}")
        logger.info(f"⏰ Heure de fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_count == total_steps:
            logger.info("🎉 PIPELINE COMPLET TERMINÉ AVEC SUCCÈS !")
            logger.info("=" * 80)
            return True
        else:
            logger.error(f"❌ PIPELINE ÉCHOUÉ - {total_steps - success_count} étape(s) échouée(s)")
            logger.error("=" * 80)
            return False

if __name__ == "__main__":
    pipeline = MLPipeline()
    pipeline.run_full_pipeline()
