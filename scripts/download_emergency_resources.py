#!/usr/bin/env python3
"""
Script pour télécharger les ressources urgences trouvées
"""

import pandas as pd
import requests
import json
import io
from pathlib import Path
import logging
from datetime import datetime
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmergencyResourceDownloader:
    def __init__(self):
        self.base_dir = Path("data")
        self.emergency_dir = self.base_dir / "processed" / "emergency_data"
        self.emergency_dir.mkdir(parents=True, exist_ok=True)
        
        # Clé API fournie
        self.api_key = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjoiNjhmZDQwYTRkMjkwNjY3Njc2Y2YzMTVhIiwidGltZSI6MTc2MTQyNzgwNi4yNjc5OTA4fQ.0RMs5OiUW1-Sg9Y7ONe-__kCJga3mP3u2sTgpIEVpCp8rH3aWHf9tS6U-VU2sMi3f7oNgUUw-Eev-ejQ6zxDDg"
        
        # Headers avec authentification
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def load_search_results(self):
        """Charge les résultats de recherche"""
        logger.info("📊 CHARGEMENT DES RÉSULTATS DE RECHERCHE")
        logger.info("=" * 50)
        
        try:
            # Lire les résultats urgences
            emergency_file = self.emergency_dir / "emergency_search_results.json"
            with open(emergency_file, 'r', encoding='utf-8') as f:
                emergency_results = json.load(f)
            
            logger.info(f"✅ Résultats urgences chargés: {len(emergency_results)} datasets")
            return emergency_results
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement résultats: {e}")
            return []
    
    def download_emergency_resources(self, datasets):
        """Télécharge les ressources urgences"""
        logger.info("📥 TÉLÉCHARGEMENT DES RESSOURCES URGENCES")
        logger.info("=" * 50)
        
        all_emergency_data = []
        
        for i, dataset in enumerate(datasets):
            try:
                logger.info(f"📊 Dataset {i+1}/{len(datasets)}: {dataset['title']}")
                
                for j, resource in enumerate(dataset['resources']):
                    if resource.get('format') in ['csv', 'json'] and resource.get('url'):
                        try:
                            logger.info(f"  📥 Ressource {j+1}: {resource['url']}")
                            
                            # Télécharger la ressource
                            response = requests.get(resource['url'], timeout=60)
                            
                            if response.status_code == 200:
                                # Traiter selon le format
                                if resource['format'] == 'csv':
                                    df = pd.read_csv(io.StringIO(response.text))
                                elif resource['format'] == 'json':
                                    json_data = response.json()
                                    if isinstance(json_data, list):
                                        df = pd.DataFrame(json_data)
                                    elif isinstance(json_data, dict):
                                        df = pd.DataFrame([json_data])
                                    else:
                                        continue
                                
                                # Ajouter des métadonnées
                                df['source_dataset'] = dataset['title']
                                df['source_organization'] = dataset['organization']
                                df['resource_url'] = resource['url']
                                df['download_date'] = datetime.now().isoformat()
                                
                                all_emergency_data.append(df)
                                logger.info(f"    ✅ Ajouté: {len(df)} lignes")
                                
                            else:
                                logger.warning(f"    ❌ Erreur téléchargement: {response.status_code}")
                        
                        except Exception as e:
                            logger.warning(f"    ❌ Erreur ressource: {e}")
                
                # Pause entre les datasets
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur dataset: {e}")
        
        # Sauvegarder les données urgences
        if all_emergency_data:
            emergency_df = pd.concat(all_emergency_data, ignore_index=True, sort=False)
            emergency_file = self.emergency_dir / "emergency_data.parquet"
            emergency_df.to_parquet(emergency_file, index=False)
            logger.info(f"💾 Données urgences sauvegardées: {emergency_file}")
            logger.info(f"📊 Total lignes: {len(emergency_df)}")
            return emergency_df
        
        return None
    
    def analyze_emergency_data(self, df):
        """Analyse les données urgences téléchargées"""
        logger.info("🔍 ANALYSE DES DONNÉES URGENCES")
        logger.info("=" * 50)
        
        try:
            logger.info(f"📊 Shape: {df.shape}")
            logger.info(f"📅 Colonnes: {list(df.columns)}")
            
            # Analyser les colonnes temporelles
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'jour' in col.lower() or 'time' in col.lower()]
            logger.info(f"📅 Colonnes temporelles: {date_cols}")
            
            # Analyser les colonnes géographiques
            geo_cols = [col for col in df.columns if 'dep' in col.lower() or 'region' in col.lower() or 'dept' in col.lower()]
            logger.info(f"🗺️ Colonnes géographiques: {geo_cols}")
            
            # Analyser les colonnes de santé
            health_cols = [col for col in df.columns if 'urg' in col.lower() or 'grippe' in col.lower() or 'covid' in col.lower() or 'syndrome' in col.lower()]
            logger.info(f"🏥 Colonnes santé: {health_cols}")
            
            # Statistiques par source
            if 'source_dataset' in df.columns:
                logger.info("📁 Par source:")
                for source in df['source_dataset'].unique():
                    count = len(df[df['source_dataset'] == source])
                    logger.info(f"  - {source}: {count:,} lignes")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            return False
    
    def run_download(self):
        """Lance le téléchargement des ressources"""
        logger.info("🚀 DÉBUT DU TÉLÉCHARGEMENT DES RESSOURCES")
        logger.info("=" * 60)
        
        # Charger les résultats de recherche
        datasets = self.load_search_results()
        
        if not datasets:
            logger.error("❌ Aucun résultat de recherche trouvé")
            return None
        
        # Télécharger les ressources
        emergency_df = self.download_emergency_resources(datasets)
        
        if emergency_df is not None:
            # Analyser les données
            self.analyze_emergency_data(emergency_df)
            logger.info("✅ TÉLÉCHARGEMENT TERMINÉ")
            logger.info("=" * 60)
            return emergency_df
        else:
            logger.warning("⚠️ Aucune donnée urgence téléchargée")
            return None

if __name__ == "__main__":
    downloader = EmergencyResourceDownloader()
    downloader.run_download()
