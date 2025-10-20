#!/usr/bin/env python3
"""
Script orchestrateur de la pipeline complète de prédiction grippe
Exécute les 3 étapes dans l'ordre : Collecte → Fusion → Entraînement
"""

import subprocess
import sys
import os
from datetime import datetime
import time

class PipelineOrchestrator:
    def __init__(self):
        """Initialise l'orchestrateur"""
        self.start_time = None
        self.scripts_dir = 'scripts'
        self.steps_completed = []
        
    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 70)
        print("🚀 PIPELINE COMPLÈTE DE PRÉDICTION GRIPPE")
        print("=" * 70)
        print()
        print("📋 Étapes à exécuter:")
        print("  1. 📊 Collecte des données (13 sources)")
        print("  2. 🔄 Fusion et création des features + FLURISK")
        print("  3. 🤖 Entraînement des modèles Random Forest (J+7, J+14, J+21, J+28)")
        print()
        print("=" * 70)
        print()
        
    def run_step(self, step_number, step_name, script_name):
        """Exécute une étape de la pipeline"""
        print(f"\n{'='*70}")
        print(f"📍 ÉTAPE {step_number}/3 : {step_name}")
        print(f"{'='*70}")
        print(f"🔧 Script: {script_name}")
        print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        step_start = time.time()
        script_path = os.path.join(self.scripts_dir, script_name)
        
        try:
            # Exécution du script
            result = subprocess.run(
                [sys.executable, script_path],
                check=True,
                capture_output=False,
                text=True
            )
            
            step_duration = time.time() - step_start
            
            print()
            print(f"✅ ÉTAPE {step_number} TERMINÉE")
            print(f"⏱️  Durée: {step_duration:.1f} secondes")
            
            self.steps_completed.append({
                'number': step_number,
                'name': step_name,
                'script': script_name,
                'duration': step_duration,
                'status': 'success'
            })
            
            return True
            
        except subprocess.CalledProcessError as e:
            step_duration = time.time() - step_start
            
            print()
            print(f"❌ ERREUR À L'ÉTAPE {step_number}")
            print(f"⏱️  Durée avant erreur: {step_duration:.1f} secondes")
            print(f"🔍 Code de sortie: {e.returncode}")
            
            self.steps_completed.append({
                'number': step_number,
                'name': step_name,
                'script': script_name,
                'duration': step_duration,
                'status': 'error',
                'error': str(e)
            })
            
            return False
            
        except FileNotFoundError:
            print()
            print(f"❌ ERREUR: Script non trouvé: {script_path}")
            print(f"💡 Vérifiez que le script existe dans le dossier '{self.scripts_dir}/'")
            
            self.steps_completed.append({
                'number': step_number,
                'name': step_name,
                'script': script_name,
                'duration': 0,
                'status': 'not_found'
            })
            
            return False
    
    def print_summary(self):
        """Affiche le résumé de l'exécution"""
        total_duration = time.time() - self.start_time
        
        print()
        print("=" * 70)
        print("📊 RÉSUMÉ DE L'EXÉCUTION")
        print("=" * 70)
        print()
        
        # Statut de chaque étape
        for step in self.steps_completed:
            status_icon = "✅" if step['status'] == 'success' else "❌"
            print(f"{status_icon} Étape {step['number']}: {step['name']}")
            print(f"   Script: {step['script']}")
            print(f"   Durée: {step['duration']:.1f}s")
            print(f"   Statut: {step['status']}")
            print()
        
        # Durée totale
        print(f"⏱️  DURÉE TOTALE: {total_duration:.1f} secondes ({total_duration/60:.1f} minutes)")
        print()
        
        # Statut final
        all_success = all(step['status'] == 'success' for step in self.steps_completed)
        
        if all_success:
            print("=" * 70)
            print("🎉 PIPELINE COMPLÈTE TERMINÉE AVEC SUCCÈS !")
            print("=" * 70)
            print()
            print("📁 Résultats disponibles:")
            print("   - Données: data/processed/dataset_grippe_*.csv")
            print("   - Modèles: models/rf_grippe_*.pkl")
            print("   - Métriques: models/metrics_*.csv")
            print("   - Prédictions: data/processed/dataset_with_predictions_*.csv")
            print()
            print("👁️  Visualiser les résultats:")
            print("   - Application web: streamlit run app.py")
            print("   - Terminal: python demo.py")
            print()
        else:
            print("=" * 70)
            print("⚠️  PIPELINE TERMINÉE AVEC ERREURS")
            print("=" * 70)
            print()
            failed_steps = [s for s in self.steps_completed if s['status'] != 'success']
            print(f"❌ {len(failed_steps)} étape(s) en erreur:")
            for step in failed_steps:
                print(f"   - Étape {step['number']}: {step['name']}")
            print()
            print("💡 Consultez les messages d'erreur ci-dessus pour plus de détails")
            print()
    
    def run(self):
        """Exécute la pipeline complète"""
        self.start_time = time.time()
        
        # En-tête
        self.print_header()
        
        # Étape 1: Collecte
        success = self.run_step(
            step_number=1,
            step_name="Collecte des données",
            script_name="collect_all_data.py"
        )
        
        if not success:
            print("\n⚠️  Arrêt de la pipeline suite à l'erreur de collecte")
            self.print_summary()
            return False
        
        # Étape 2: Fusion
        success = self.run_step(
            step_number=2,
            step_name="Fusion et features + FLURISK",
            script_name="fuse_data.py"
        )
        
        if not success:
            print("\n⚠️  Arrêt de la pipeline suite à l'erreur de fusion")
            self.print_summary()
            return False
        
        # Étape 3: Entraînement
        success = self.run_step(
            step_number=3,
            step_name="Entraînement des modèles",
            script_name="train_model.py"
        )
        
        if not success:
            print("\n⚠️  Erreur lors de l'entraînement des modèles")
            self.print_summary()
            return False
        
        # Résumé final
        self.print_summary()
        return True

def main():
    """Fonction principale"""
    # Vérification du répertoire
    if not os.path.exists('scripts'):
        print("❌ ERREUR: Le dossier 'scripts/' n'existe pas")
        print("💡 Exécutez ce script depuis la racine du projet")
        sys.exit(1)
    
    # Création de l'orchestrateur
    orchestrator = PipelineOrchestrator()
    
    # Exécution de la pipeline
    success = orchestrator.run()
    
    # Code de sortie
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
