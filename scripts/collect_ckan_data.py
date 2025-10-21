#!/usr/bin/env python3
"""
Collecte de données réelles via l'API CKAN
Sources gouvernementales françaises
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

class CKANDataCollector:
    def __init__(self):
        # Sites CKAN français connus avec bonnes URLs
        self.ckan_sites = {
            'data.gouv.fr': 'https://www.data.gouv.fr/api/1',
            'opendata.paris': 'https://opendata.paris.fr/api/3/action',
            'data.grandlyon.com': 'https://data.grandlyon.com/api/3/action',
            'data.montpellier3m.fr': 'https://data.montpellier3m.fr/api/3/action'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LUMEN-System/1.0 (Health Surveillance)',
            'Accept': 'application/json'
        })
    
    def search_datasets(self, site_url, query="grippe", limit=10):
        """Rechercher des datasets sur un site CKAN"""
        try:
            # Construire l'URL correcte selon le site
            if 'data.gouv.fr' in site_url:
                url = f"{site_url}/datasets"
                params = {'q': query, 'page_size': limit}
            else:
                url = f"{site_url}/package_search"
                params = {
                    'q': query,
                    'rows': limit,
                    'facet.field': ['organization', 'tags']
                }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('result', {}).get('results', [])
            else:
                print(f"❌ Erreur API {site_url}: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur connexion {site_url}: {e}")
            return []
    
    def get_dataset_details(self, site_url, dataset_id):
        """Récupérer les détails d'un dataset"""
        try:
            url = f"{site_url}/action/package_show"
            params = {'id': dataset_id}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('result')
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erreur détails dataset {dataset_id}: {e}")
            return None
    
    def download_resource(self, resource_url, filename):
        """Télécharger une ressource"""
        try:
            response = self.session.get(resource_url, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"❌ Erreur téléchargement {resource_url}: {e}")
            return False
    
    def collect_health_data(self):
        """Collecter les données de santé"""
        print("🏥 COLLECTE DE DONNÉES DE SANTÉ RÉELLES")
        print("=" * 50)
        
        health_datasets = []
        
        for site_name, site_url in self.ckan_sites.items():
            print(f"\n🔍 Recherche sur {site_name}...")
            
            # Rechercher des datasets liés à la santé
            queries = [
                "grippe",
                "santé publique", 
                "surveillance",
                "épidémie",
                "vaccination",
                "urgences",
                "hospitalisation"
            ]
            
            for query in queries:
                datasets = self.search_datasets(site_url, query, limit=5)
                
                for dataset in datasets:
                    dataset_id = dataset.get('id')
                    title = dataset.get('title', 'Sans titre')
                    organization = dataset.get('organization', {}).get('title', 'Inconnu')
                    
                    print(f"  📊 {title} ({organization})")
                    
                    # Récupérer les détails
                    details = self.get_dataset_details(site_url, dataset_id)
                    if details:
                        resources = details.get('resources', [])
                        for resource in resources:
                            if resource.get('format', '').upper() in ['CSV', 'XLS', 'XLSX', 'JSON']:
                                resource_url = resource.get('url')
                                resource_name = resource.get('name', 'resource')
                                
                                # Télécharger la ressource
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                filename = f"data/ckan/{site_name}_{timestamp}_{resource_name}.{resource.get('format', 'csv').lower()}"
                                
                                if self.download_resource(resource_url, filename):
                                    health_datasets.append({
                                        'site': site_name,
                                        'dataset_id': dataset_id,
                                        'title': title,
                                        'organization': organization,
                                        'resource_name': resource_name,
                                        'resource_url': resource_url,
                                        'filename': filename,
                                        'format': resource.get('format', 'CSV'),
                                        'size': resource.get('size', 0)
                                    })
                                    print(f"    ✅ Téléchargé: {filename}")
                                
                                time.sleep(1)  # Respecter les limites de taux
        
        return health_datasets
    
    def collect_demographic_data(self):
        """Collecter les données démographiques"""
        print("\n👥 COLLECTE DE DONNÉES DÉMOGRAPHIQUES")
        print("=" * 50)
        
        demographic_datasets = []
        
        for site_name, site_url in self.ckan_sites.items():
            print(f"\n🔍 Recherche démographie sur {site_name}...")
            
            queries = [
                "population",
                "démographie", 
                "recensement",
                "INSEE",
                "commune",
                "département",
                "région"
            ]
            
            for query in queries:
                datasets = self.search_datasets(site_url, query, limit=3)
                
                for dataset in datasets:
                    dataset_id = dataset.get('id')
                    title = dataset.get('title', 'Sans titre')
                    
                    print(f"  📊 {title}")
                    
                    details = self.get_dataset_details(site_url, dataset_id)
                    if details:
                        resources = details.get('resources', [])
                        for resource in resources:
                            if resource.get('format', '').upper() in ['CSV', 'XLS', 'XLSX']:
                                resource_url = resource.get('url')
                                resource_name = resource.get('name', 'resource')
                                
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                filename = f"data/ckan/{site_name}_demo_{timestamp}_{resource_name}.{resource.get('format', 'csv').lower()}"
                                
                                if self.download_resource(resource_url, filename):
                                    demographic_datasets.append({
                                        'site': site_name,
                                        'dataset_id': dataset_id,
                                        'title': title,
                                        'filename': filename,
                                        'format': resource.get('format', 'CSV')
                                    })
                                    print(f"    ✅ Téléchargé: {filename}")
                                
                                time.sleep(1)
        
        return demographic_datasets
    
    def process_health_data(self, health_datasets):
        """Traiter les données de santé téléchargées"""
        print("\n🔄 TRAITEMENT DES DONNÉES DE SANTÉ")
        print("=" * 50)
        
        processed_data = []
        
        for dataset in health_datasets:
            try:
                filename = dataset['filename']
                print(f"\n📊 Traitement: {filename}")
                
                # Lire le fichier selon son format
                if filename.endswith('.csv'):
                    df = pd.read_csv(filename, encoding='utf-8', low_memory=False)
                elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                    df = pd.read_excel(filename)
                else:
                    print(f"  ⚠️ Format non supporté: {filename}")
                    continue
                
                print(f"  📈 {len(df)} lignes, {len(df.columns)} colonnes")
                print(f"  📋 Colonnes: {list(df.columns)[:5]}...")
                
                # Analyser le contenu pour détecter les données de grippe
                grippe_keywords = ['grippe', 'syndrome', 'grippal', 'influenza', 'virus']
                relevant_columns = []
                
                for col in df.columns:
                    if any(keyword in str(col).lower() for keyword in grippe_keywords):
                        relevant_columns.append(col)
                
                if relevant_columns:
                    print(f"  🎯 Colonnes pertinentes: {relevant_columns}")
                    
                    # Extraire les données pertinentes
                    sample_data = df[relevant_columns].head(10)
                    print(f"  📊 Échantillon:\n{sample_data}")
                    
                    processed_data.append({
                        'source': dataset['site'],
                        'title': dataset['title'],
                        'filename': filename,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'relevant_columns': relevant_columns,
                        'data': df
                    })
                else:
                    print(f"  ⚠️ Aucune donnée de grippe détectée")
                
            except Exception as e:
                print(f"  ❌ Erreur traitement {filename}: {e}")
        
        return processed_data
    
    def save_collection_report(self, health_datasets, demographic_datasets, processed_data):
        """Sauvegarder le rapport de collecte"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            'timestamp': timestamp,
            'collection_date': datetime.now().isoformat(),
            'health_datasets': len(health_datasets),
            'demographic_datasets': len(demographic_datasets),
            'processed_datasets': len(processed_data),
            'health_files': [d['filename'] for d in health_datasets],
            'demographic_files': [d['filename'] for d in demographic_datasets],
            'processed_files': [d['filename'] for d in processed_data]
        }
        
        with open(f'data/ckan/collection_report_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Rapport sauvegardé: data/ckan/collection_report_{timestamp}.json")
        return report

def main():
    """Fonction principale"""
    print("🚀 COLLECTE DE DONNÉES RÉELLES VIA CKAN")
    print("=" * 60)
    print(f"⏰ Début: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Créer le dossier de collecte
    os.makedirs('data/ckan', exist_ok=True)
    
    # Initialiser le collecteur
    collector = CKANDataCollector()
    
    try:
        # Collecter les données de santé
        health_datasets = collector.collect_health_data()
        
        # Collecter les données démographiques
        demographic_datasets = collector.collect_demographic_data()
        
        # Traiter les données de santé
        processed_data = collector.process_health_data(health_datasets)
        
        # Sauvegarder le rapport
        report = collector.save_collection_report(health_datasets, demographic_datasets, processed_data)
        
        print(f"\n🎉 COLLECTE TERMINÉE")
        print(f"📊 Datasets santé: {report['health_datasets']}")
        print(f"👥 Datasets démographie: {report['demographic_datasets']}")
        print(f"🔄 Datasets traités: {report['processed_datasets']}")
        print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
