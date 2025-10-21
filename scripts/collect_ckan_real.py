#!/usr/bin/env python3
"""
Collecte de données réelles via l'API CKAN
Utilisation correcte de l'API CKAN selon la documentation
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

class CKANRealCollector:
    def __init__(self):
        # Sites CKAN français avec URLs correctes
        self.ckan_sites = {
            'data.gouv.fr': {
                'base_url': 'https://www.data.gouv.fr/api/1',
                'api_version': '1',
                'search_endpoint': 'datasets'
            },
            'opendata.paris': {
                'base_url': 'https://opendata.paris.fr/api/3/action',
                'api_version': '3',
                'search_endpoint': 'package_search'
            },
            'data.grandlyon.com': {
                'base_url': 'https://data.grandlyon.com/api/3/action',
                'api_version': '3',
                'search_endpoint': 'package_search'
            },
            'data.montpellier3m.fr': {
                'base_url': 'https://data.montpellier3m.fr/api/3/action',
                'api_version': '3',
                'search_endpoint': 'package_search'
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LUMEN-System/1.0 (Health Surveillance)',
            'Accept': 'application/json'
        })
    
    def test_ckan_connection(self, site_name, site_config):
        """Tester la connexion à un site CKAN"""
        try:
            if site_config['api_version'] == '1':
                # API v1 (data.gouv.fr)
                url = f"{site_config['base_url']}/datasets"
                response = self.session.get(url, timeout=10)
            else:
                # API v3 (CKAN standard)
                url = f"{site_config['base_url']}/package_list"
                response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {site_name}: Connexion OK")
                return True
            else:
                print(f"❌ {site_name}: Erreur {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {site_name}: {e}")
            return False
    
    def search_datasets_v1(self, site_config, query, limit=10):
        """Rechercher des datasets avec API v1 (data.gouv.fr)"""
        try:
            url = f"{site_config['base_url']}/datasets"
            params = {
                'q': query,
                'page_size': limit,
                'sort': '-created'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                return []
                
        except Exception as e:
            print(f"❌ Erreur recherche v1: {e}")
            return []
    
    def search_datasets_v3(self, site_config, query, limit=10):
        """Rechercher des datasets avec API v3 (CKAN standard)"""
        try:
            url = f"{site_config['base_url']}/package_search"
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
                print(f"❌ Erreur API: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur recherche v3: {e}")
            return []
    
    def get_dataset_details_v1(self, site_config, dataset_id):
        """Récupérer les détails d'un dataset avec API v1"""
        try:
            url = f"{site_config['base_url']}/datasets/{dataset_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Erreur détails v1: {e}")
            return None
    
    def get_dataset_details_v3(self, site_config, dataset_id):
        """Récupérer les détails d'un dataset avec API v3"""
        try:
            url = f"{site_config['base_url']}/package_show"
            params = {'id': dataset_id}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('result')
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erreur détails v3: {e}")
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
        """Collecter les données de santé via CKAN"""
        print("🏥 COLLECTE DE DONNÉES DE SANTÉ VIA CKAN")
        print("=" * 50)
        
        health_datasets = []
        
        for site_name, site_config in self.ckan_sites.items():
            print(f"\n🔍 Test connexion {site_name}...")
            
            # Tester la connexion
            if not self.test_ckan_connection(site_name, site_config):
                continue
            
            print(f"📊 Recherche sur {site_name}...")
            
            # Rechercher des datasets liés à la santé
            queries = [
                "grippe",
                "santé publique", 
                "surveillance",
                "épidémie",
                "vaccination",
                "urgences",
                "hospitalisation",
                "médical",
                "santé"
            ]
            
            for query in queries:
                print(f"  🔍 Recherche: '{query}'")
                
                # Utiliser la bonne API selon la version
                if site_config['api_version'] == '1':
                    datasets = self.search_datasets_v1(site_config, query, limit=5)
                else:
                    datasets = self.search_datasets_v3(site_config, query, limit=5)
                
                print(f"    📊 {len(datasets)} datasets trouvés")
                
                for dataset in datasets:
                    dataset_id = dataset.get('id') or dataset.get('slug')
                    title = dataset.get('title', 'Sans titre')
                    organization = dataset.get('organization', {})
                    if isinstance(organization, dict):
                        org_name = organization.get('title', organization.get('name', 'Inconnu'))
                    else:
                        org_name = str(organization)
                    
                    print(f"    📋 {title} ({org_name})")
                    
                    # Récupérer les détails
                    if site_config['api_version'] == '1':
                        details = self.get_dataset_details_v1(site_config, dataset_id)
                    else:
                        details = self.get_dataset_details_v3(site_config, dataset_id)
                    
                    if details:
                        # Traiter les ressources selon la version d'API
                        if site_config['api_version'] == '1':
                            resources = details.get('resources', [])
                        else:
                            resources = details.get('resources', [])
                        
                        for resource in resources:
                            if resource.get('format', '').upper() in ['CSV', 'XLS', 'XLSX', 'JSON', 'XML']:
                                resource_url = resource.get('url')
                                resource_name = resource.get('name', 'resource')
                                
                                # Télécharger la ressource
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                file_ext = resource.get('format', 'csv').lower()
                                filename = f"data/ckan/{site_name}_{timestamp}_{resource_name}.{file_ext}"
                                
                                print(f"      📥 Téléchargement: {resource_name}")
                                if self.download_resource(resource_url, filename):
                                    health_datasets.append({
                                        'site': site_name,
                                        'dataset_id': dataset_id,
                                        'title': title,
                                        'organization': org_name,
                                        'resource_name': resource_name,
                                        'resource_url': resource_url,
                                        'filename': filename,
                                        'format': resource.get('format', 'CSV'),
                                        'size': resource.get('size', 0)
                                    })
                                    print(f"        ✅ Téléchargé: {filename}")
                                
                                time.sleep(1)  # Respecter les limites de taux
        
        return health_datasets
    
    def collect_demographic_data(self):
        """Collecter les données démographiques via CKAN"""
        print("\n👥 COLLECTE DE DONNÉES DÉMOGRAPHIQUES VIA CKAN")
        print("=" * 50)
        
        demographic_datasets = []
        
        for site_name, site_config in self.ckan_sites.items():
            print(f"\n🔍 Recherche démographie sur {site_name}...")
            
            if not self.test_ckan_connection(site_name, site_config):
                continue
            
            queries = [
                "population",
                "démographie", 
                "recensement",
                "INSEE",
                "commune",
                "département",
                "région",
                "habitants"
            ]
            
            for query in queries:
                print(f"  🔍 Recherche: '{query}'")
                
                if site_config['api_version'] == '1':
                    datasets = self.search_datasets_v1(site_config, query, limit=3)
                else:
                    datasets = self.search_datasets_v3(site_config, query, limit=3)
                
                print(f"    📊 {len(datasets)} datasets trouvés")
                
                for dataset in datasets:
                    dataset_id = dataset.get('id') or dataset.get('slug')
                    title = dataset.get('title', 'Sans titre')
                    
                    print(f"    📋 {title}")
                    
                    if site_config['api_version'] == '1':
                        details = self.get_dataset_details_v1(site_config, dataset_id)
                    else:
                        details = self.get_dataset_details_v3(site_config, dataset_id)
                    
                    if details:
                        if site_config['api_version'] == '1':
                            resources = details.get('resources', [])
                        else:
                            resources = details.get('resources', [])
                        
                        for resource in resources:
                            if resource.get('format', '').upper() in ['CSV', 'XLS', 'XLSX']:
                                resource_url = resource.get('url')
                                resource_name = resource.get('name', 'resource')
                                
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                file_ext = resource.get('format', 'csv').lower()
                                filename = f"data/ckan/{site_name}_demo_{timestamp}_{resource_name}.{file_ext}"
                                
                                print(f"      📥 Téléchargement: {resource_name}")
                                if self.download_resource(resource_url, filename):
                                    demographic_datasets.append({
                                        'site': site_name,
                                        'dataset_id': dataset_id,
                                        'title': title,
                                        'filename': filename,
                                        'format': resource.get('format', 'CSV')
                                    })
                                    print(f"        ✅ Téléchargé: {filename}")
                                
                                time.sleep(1)
        
        return demographic_datasets
    
    def process_downloaded_data(self, health_datasets, demographic_datasets):
        """Traiter les données téléchargées"""
        print("\n🔄 TRAITEMENT DES DONNÉES TÉLÉCHARGÉES")
        print("=" * 50)
        
        processed_data = []
        
        all_datasets = health_datasets + demographic_datasets
        
        for dataset in all_datasets:
            try:
                filename = dataset['filename']
                print(f"\n📊 Traitement: {filename}")
                
                # Lire le fichier selon son format
                if filename.endswith('.csv'):
                    df = pd.read_csv(filename, encoding='utf-8', low_memory=False)
                elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                    df = pd.read_excel(filename)
                elif filename.endswith('.json'):
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
                else:
                    print(f"  ⚠️ Format non supporté: {filename}")
                    continue
                
                print(f"  📈 {len(df)} lignes, {len(df.columns)} colonnes")
                print(f"  📋 Colonnes: {list(df.columns)[:5]}...")
                
                # Analyser le contenu
                health_keywords = ['grippe', 'syndrome', 'grippal', 'influenza', 'virus', 'santé', 'médical']
                demo_keywords = ['population', 'habitants', 'commune', 'département', 'région']
                
                relevant_columns = []
                for col in df.columns:
                    col_lower = str(col).lower()
                    if any(keyword in col_lower for keyword in health_keywords + demo_keywords):
                        relevant_columns.append(col)
                
                if relevant_columns:
                    print(f"  🎯 Colonnes pertinentes: {relevant_columns}")
                    
                    # Extraire les données pertinentes
                    sample_data = df[relevant_columns].head(5)
                    print(f"  📊 Échantillon:\n{sample_data}")
                    
                    processed_data.append({
                        'source': dataset['site'],
                        'title': dataset['title'],
                        'filename': filename,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'relevant_columns': relevant_columns,
                        'data': df,
                        'type': 'health' if any(keyword in str(dataset.get('title', '')).lower() for keyword in health_keywords) else 'demographic'
                    })
                else:
                    print(f"  ⚠️ Aucune donnée pertinente détectée")
                
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
            'processed_files': [d['filename'] for d in processed_data],
            'sites_accessed': list(set([d['site'] for d in health_datasets + demographic_datasets]))
        }
        
        os.makedirs('data/ckan', exist_ok=True)
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
    collector = CKANRealCollector()
    
    try:
        # Collecter les données de santé
        health_datasets = collector.collect_health_data()
        
        # Collecter les données démographiques
        demographic_datasets = collector.collect_demographic_data()
        
        # Traiter les données téléchargées
        processed_data = collector.process_downloaded_data(health_datasets, demographic_datasets)
        
        # Sauvegarder le rapport
        report = collector.save_collection_report(health_datasets, demographic_datasets, processed_data)
        
        print(f"\n🎉 COLLECTE TERMINÉE")
        print(f"📊 Datasets santé: {report['health_datasets']}")
        print(f"👥 Datasets démographie: {report['demographic_datasets']}")
        print(f"🔄 Datasets traités: {report['processed_datasets']}")
        print(f"🌐 Sites accessibles: {', '.join(report['sites_accessed'])}")
        print(f"⏰ Fin: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
