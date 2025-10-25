#!/usr/bin/env python3
"""
Script pour récupérer les données manquantes : urgences, données départementales
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

class EmergencyDataCollector:
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
    
    def search_emergency_datasets(self):
        """Recherche les datasets urgences sur data.gouv.fr"""
        logger.info("🏥 RECHERCHE DES DONNÉES URGENCES")
        logger.info("=" * 50)
        
        # Mots-clés pour la recherche urgences
        emergency_keywords = [
            "urgences syndromes grippaux",
            "OSCOUR urgences",
            "passages urgences grippe",
            "urgences hospitalières",
            "syndromes grippaux urgences",
            "données urgences SPF",
            "surveillance grippe urgences",
            "urgences épidémie"
        ]
        
        all_datasets = []
        
        for keyword in emergency_keywords:
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
        search_file = self.emergency_dir / "emergency_search_results.json"
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump(all_datasets, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats de recherche sauvegardés: {search_file}")
        return all_datasets
    
    def search_departmental_datasets(self):
        """Recherche les datasets départementaux"""
        logger.info("🗺️ RECHERCHE DES DONNÉES DÉPARTEMENTALES")
        logger.info("=" * 50)
        
        # Mots-clés pour la recherche départementale
        departmental_keywords = [
            "données départementales",
            "département France",
            "données territoriales",
            "département population",
            "département santé",
            "ARS département",
            "données régionales départementales"
        ]
        
        all_datasets = []
        
        for keyword in departmental_keywords:
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
        search_file = self.emergency_dir / "departmental_search_results.json"
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump(all_datasets, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats de recherche sauvegardés: {search_file}")
        return all_datasets
    
    def download_emergency_resources(self, datasets):
        """Télécharge les ressources urgences trouvées"""
        logger.info("📥 TÉLÉCHARGEMENT DES RESSOURCES URGENCES")
        logger.info("=" * 50)
        
        all_emergency_data = []
        
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
            return emergency_df
        
        return None
    
    def download_departmental_resources(self, datasets):
        """Télécharge les ressources départementales trouvées"""
        logger.info("📥 TÉLÉCHARGEMENT DES RESSOURCES DÉPARTEMENTALES")
        logger.info("=" * 50)
        
        all_departmental_data = []
        
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
                                
                                all_departmental_data.append(df)
                                logger.info(f"    ✅ Ajouté: {len(df)} lignes")
                                
                            else:
                                logger.warning(f"    ❌ Erreur téléchargement: {response.status_code}")
                        
                        except Exception as e:
                            logger.warning(f"    ❌ Erreur ressource: {e}")
                
                # Pause entre les datasets
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur dataset: {e}")
        
        # Sauvegarder les données départementales
        if all_departmental_data:
            departmental_df = pd.concat(all_departmental_data, ignore_index=True, sort=False)
            departmental_file = self.emergency_dir / "departmental_data.parquet"
            departmental_df.to_parquet(departmental_file, index=False)
            logger.info(f"💾 Données départementales sauvegardées: {departmental_file}")
            return departmental_df
        
        return None
    
    def run_collection(self):
        """Lance la collecte des données manquantes"""
        logger.info("🚀 DÉBUT DE LA COLLECTE DES DONNÉES MANQUANTES")
        logger.info("=" * 60)
        
        # Rechercher les datasets urgences
        emergency_datasets = self.search_emergency_datasets()
        
        if emergency_datasets:
            logger.info(f"📊 {len(emergency_datasets)} datasets urgences trouvés")
            
            # Télécharger les ressources urgences
            emergency_df = self.download_emergency_resources(emergency_datasets)
            
            if emergency_df is not None:
                logger.info(f"✅ Collecte urgences terminée: {len(emergency_df)} lignes")
            else:
                logger.warning("⚠️ Aucune donnée urgence téléchargée")
        
        # Rechercher les datasets départementaux
        departmental_datasets = self.search_departmental_datasets()
        
        if departmental_datasets:
            logger.info(f"📊 {len(departmental_datasets)} datasets départementaux trouvés")
            
            # Télécharger les ressources départementales
            departmental_df = self.download_departmental_resources(departmental_datasets)
            
            if departmental_df is not None:
                logger.info(f"✅ Collecte départementale terminée: {len(departmental_df)} lignes")
            else:
                logger.warning("⚠️ Aucune donnée départementale téléchargée")
        
        logger.info("✅ COLLECTE TERMINÉE")
        logger.info("=" * 60)

if __name__ == "__main__":
    import io
    collector = EmergencyDataCollector()
    collector.run_collection()
