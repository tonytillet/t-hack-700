#!/usr/bin/env python3
"""
Script pour collecter les données météo via data.gouv.fr avec la clé API fournie
"""

import pandas as pd
import requests
import json
from pathlib import Path
import logging
from datetime import datetime
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataCollector:
    def __init__(self):
        self.base_dir = Path("data")
        self.external_dir = self.base_dir / "processed" / "external_data"
        self.external_dir.mkdir(parents=True, exist_ok=True)
        
        # Clé API fournie
        self.api_key = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyIjoiNjhmZDQwYTRkMjkwNjY3Njc2Y2YzMTVhIiwidGltZSI6MTc2MTQyNzgwNi4yNjc5OTA4fQ.0RMs5OiUW1-Sg9Y7ONe-__kCJga3mP3u2sTgpIEVpCp8rH3aWHf9tS6U-VU2sMi3f7oNgUUw-Eev-ejQ6zxDDg"
        
        # Headers avec authentification
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search_weather_datasets(self):
        """Recherche les datasets météo sur data.gouv.fr"""
        logger.info("🔍 RECHERCHE DES DONNÉES MÉTÉO SUR DATA.GOUV.FR")
        logger.info("=" * 50)
        
        # Mots-clés pour la recherche météo
        weather_keywords = [
            "météo température",
            "données météorologiques",
            "température France",
            "humidité météo",
            "précipitations météo",
            "données climatiques",
            "météo France",
            "température régionale"
        ]
        
        all_datasets = []
        
        for keyword in weather_keywords:
            try:
                logger.info(f"🔍 Recherche: {keyword}")
                
                # API data.gouv.fr
                url = "https://www.data.gouv.fr/api/1/datasets/"
                params = {
                    "q": keyword,
                    "page_size": 20,
                    "sort": "-created"
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    datasets = data.get('data', [])
                    
                    logger.info(f"✅ Trouvé {len(datasets)} datasets pour '{keyword}'")
                    
                    for dataset in datasets:
                        all_datasets.append({
                            'title': dataset.get('title', ''),
                            'description': dataset.get('description', ''),
                            'organization': dataset.get('organization', {}).get('name', ''),
                            'resources': dataset.get('resources', []),
                            'created': dataset.get('created', ''),
                            'keyword': keyword
                        })
                else:
                    logger.warning(f"❌ Erreur recherche '{keyword}': {response.status_code}")
                
                # Pause entre les requêtes
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erreur recherche '{keyword}': {e}")
        
        # Sauvegarder les résultats de recherche
        search_file = self.external_dir / "weather_search_results.json"
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump(all_datasets, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats de recherche sauvegardés: {search_file}")
        return all_datasets
    
    def download_weather_resources(self, datasets):
        """Télécharge les ressources météo trouvées"""
        logger.info("📥 TÉLÉCHARGEMENT DES RESSOURCES MÉTÉO")
        logger.info("=" * 50)
        
        all_weather_data = []
        
        for dataset in datasets:
            try:
                logger.info(f"📊 Dataset: {dataset['title']}")
                
                for resource in dataset['resources']:
                    if resource.get('format') in ['csv', 'json'] and resource.get('url'):
                        try:
                            logger.info(f"  📥 Téléchargement: {resource['url']}")
                            
                            # Télécharger la ressource
                            response = requests.get(resource['url'], timeout=30)
                            
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
                                
                                all_weather_data.append(df)
                                logger.info(f"    ✅ Ajouté: {len(df)} lignes")
                                
                            else:
                                logger.warning(f"    ❌ Erreur téléchargement: {response.status_code}")
                        
                        except Exception as e:
                            logger.warning(f"    ❌ Erreur ressource: {e}")
                
                # Pause entre les datasets
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur dataset: {e}")
        
        # Sauvegarder les données météo
        if all_weather_data:
            weather_df = pd.concat(all_weather_data, ignore_index=True, sort=False)
            weather_file = self.external_dir / "weather_data_gouv.parquet"
            weather_df.to_parquet(weather_file, index=False)
            logger.info(f"💾 Données météo sauvegardées: {weather_file}")
            return weather_df
        
        return None
    
    def run_collection(self):
        """Lance la collecte des données météo"""
        logger.info("🚀 DÉBUT DE LA COLLECTE MÉTÉO VIA DATA.GOUV.FR")
        logger.info("=" * 60)
        
        # Rechercher les datasets météo
        datasets = self.search_weather_datasets()
        
        if datasets:
            logger.info(f"📊 {len(datasets)} datasets météo trouvés")
            
            # Télécharger les ressources
            weather_df = self.download_weather_resources(datasets)
            
            if weather_df is not None:
                logger.info(f"✅ Collecte terminée: {len(weather_df)} lignes de données météo")
            else:
                logger.warning("⚠️ Aucune donnée météo téléchargée")
        else:
            logger.warning("⚠️ Aucun dataset météo trouvé")

if __name__ == "__main__":
    import io
    collector = WeatherDataCollector()
    collector.run_collection()
