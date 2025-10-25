#!/usr/bin/env python3
"""
Script de collecte automatisée de données pour LUMEN
Collecte les données depuis data.gouv.fr, Open-Meteo, Wikipedia, etc.
"""

import requests
import json
import os
import time
from datetime import datetime
import wikipediaapi
from pathlib import Path

class DataCollector:
    def __init__(self):
        self.base_dir = Path("data/raw")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des APIs
        self.data_gouv_url = "https://www.data.gouv.fr/api/1/datasets/"
        self.open_meteo_url = "https://api.open-meteo.com/v1/forecast"
        
        # Configuration Wikipedia
        self.wiki = wikipediaapi.Wikipedia(
            language='fr',
            user_agent='LUMEN-DataCollector/1.0'
        )
        
        # Logs
        self.log_file = self.base_dir / "logs" / f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log(self, message):
        """Log un message avec timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def collect_data_gouv_fr(self):
        """Collecte les données depuis data.gouv.fr"""
        self.log("🦠 Collecte des données data.gouv.fr...")
        
        # Recherches à effectuer
        searches = [
            "grippe syndromes grippaux spf",
            "oscour urgences grippe", 
            "vaccination grippe",
            "météo france température humidité",
            "insee population région",
            "mobilité domicile travail",
            "pharmacies officines france",
            "stock vaccin grippe",
            "ansm ventes paracetamol grippe",
            "wikipedia santé grippe",
            "twitter santé grippe",
            "capacité hospitalière lits hôpital",
            "hopitaux urgences",
            "absentéisme maladie dares",
            "arrêt maladie cnam"
        ]
        
        results = {}
        for search in searches:
            try:
                self.log(f"  Recherche: {search}")
                response = requests.get(
                    self.data_gouv_url,
                    params={"q": search, "page_size": 20},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results[search] = data
                    
                    # Sauvegarder le résultat
                    filename = search.replace(" ", "_").replace("/", "_") + ".json"
                    filepath = self.base_dir / "data_gouv_fr" / filename
                    filepath.parent.mkdir(exist_ok=True)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    self.log(f"    ✅ Sauvegardé: {filename} ({len(data.get('data', []))} résultats)")
                else:
                    self.log(f"    ❌ Erreur HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"    ❌ Erreur: {str(e)}")
            
            # Pause entre les requêtes
            time.sleep(1)
        
        return results
    
    def collect_weather_data(self):
        """Collecte les données météo depuis Open-Meteo"""
        self.log("🌦️ Collecte des données météo...")
        
        # Villes françaises principales
        cities = [
            {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
            {"name": "Lyon", "lat": 45.7640, "lon": 4.8357},
            {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
            {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442},
            {"name": "Nice", "lat": 43.7102, "lon": 7.2620}
        ]
        
        weather_data = {}
        
        for city in cities:
            try:
                self.log(f"  Météo pour {city['name']}...")
                
                response = requests.get(
                    self.open_meteo_url,
                    params={
                        "latitude": city["lat"],
                        "longitude": city["lon"],
                        "current": "temperature_2m,relative_humidity_2m,precipitation",
                        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                        "timezone": "Europe/Paris",
                        "forecast_days": 7
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data[city["name"]] = data
                    self.log(f"    ✅ Données météo récupérées pour {city['name']}")
                else:
                    self.log(f"    ❌ Erreur HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"    ❌ Erreur météo {city['name']}: {str(e)}")
            
            time.sleep(0.5)
        
        # Sauvegarder les données météo
        filepath = self.base_dir / "other" / "donnees_meteo.json"
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ Données météo sauvegardées: {filepath}")
        return weather_data
    
    def collect_wikipedia_data(self):
        """Collecte les données depuis Wikipedia"""
        self.log("🧠 Collecte des données Wikipedia...")
        
        # Pages Wikipedia santé à récupérer
        pages = [
            "Grippe",
            "Épidémie de grippe",
            "Vaccin antigrippal",
            "Santé publique en France",
            "Institut Pasteur",
            "Santé publique France",
            "Agence nationale de sécurité du médicament",
            "Direction de la recherche, des études, de l'évaluation et des statistiques",
            "Ministère de la Santé (France)",
            "Système de santé français",
            "Prévention des maladies",
            "Surveillance épidémiologique"
        ]
        
        wiki_data = {}
        
        for page_title in pages:
            try:
                self.log(f"  Page: {page_title}")
                page = self.wiki.page(page_title)
                
                if page.exists():
                    wiki_data[page_title] = {
                        "title": page.title,
                        "summary": page.summary,
                        "text": page.text[:5000],  # Limiter la taille
                        "url": page.fullurl,
                        "categories": list(page.categories.keys())[:10]  # Limiter les catégories
                    }
                    self.log(f"    ✅ Page récupérée: {page_title}")
                else:
                    self.log(f"    ❌ Page non trouvée: {page_title}")
                    
            except Exception as e:
                self.log(f"    ❌ Erreur Wikipedia {page_title}: {str(e)}")
            
            time.sleep(1)
        
        # Sauvegarder les données Wikipedia
        filepath = self.base_dir / "other" / "wikipedia_sante.json"
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(wiki_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ Données Wikipedia sauvegardées: {filepath}")
        return wiki_data
    
    def collect_insee_data(self):
        """Collecte les données INSEE (structure seulement)"""
        self.log("👥 Collecte des données INSEE...")
        
        try:
            # Test de l'API MELODI INSEE
            melodi_url = "https://api.insee.fr/metadonnees/V1/codes/cog/communes"
            
            response = requests.get(melodi_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Sauvegarder la structure
                filepath = self.base_dir / "insee" / "melodi_structure.json"
                filepath.parent.mkdir(exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.log(f"✅ Structure INSEE sauvegardée: {filepath}")
                return data
            else:
                self.log(f"❌ Erreur INSEE HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Erreur INSEE: {str(e)}")
        
        return {}
    
    def create_summary(self, all_data):
        """Crée un résumé de toutes les données collectées"""
        self.log("📊 Création du résumé...")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(all_data),
            "sources": {},
            "statistics": {
                "total_files": 0,
                "total_size_mb": 0,
                "success_rate": 0
            }
        }
        
        # Analyser chaque source
        for source, data in all_data.items():
            if isinstance(data, dict):
                summary["sources"][source] = {
                    "type": "dict",
                    "keys": len(data.keys()),
                    "status": "success"
                }
            elif isinstance(data, list):
                summary["sources"][source] = {
                    "type": "list", 
                    "items": len(data),
                    "status": "success"
                }
        
        # Sauvegarder le résumé
        filepath = self.base_dir / "summary.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ Résumé créé: {filepath}")
        return summary
    
    def run_collection(self):
        """Lance la collecte complète"""
        self.log("🚀 DÉBUT DE LA COLLECTE DE DONNÉES LUMEN")
        self.log("=" * 50)
        
        all_data = {}
        
        try:
            # 1. Collecte data.gouv.fr
            data_gouv_results = self.collect_data_gouv_fr()
            all_data["data_gouv_fr"] = data_gouv_results
            
            # 2. Collecte météo
            weather_data = self.collect_weather_data()
            all_data["weather"] = weather_data
            
            # 3. Collecte Wikipedia
            wiki_data = self.collect_wikipedia_data()
            all_data["wikipedia"] = wiki_data
            
            # 4. Collecte INSEE
            insee_data = self.collect_insee_data()
            all_data["insee"] = insee_data
            
            # 5. Créer le résumé
            summary = self.create_summary(all_data)
            all_data["summary"] = summary
            
            self.log("=" * 50)
            self.log("✅ COLLECTE TERMINÉE AVEC SUCCÈS")
            self.log(f"📊 Résumé sauvegardé dans: {self.log_file}")
            
        except Exception as e:
            self.log(f"❌ ERREUR CRITIQUE: {str(e)}")
            raise
        
        return all_data

def main():
    """Point d'entrée principal"""
    print("🔍 LUMEN - Collecte de données automatisée")
    print("=" * 50)
    
    collector = DataCollector()
    results = collector.run_collection()
    
    print("\n🎯 COLLECTE TERMINÉE")
    print("=" * 50)
    print(f"📁 Données sauvegardées dans: data/raw/")
    print(f"📝 Logs disponibles dans: {collector.log_file}")
    print(f"📊 Résumé: {len(results)} sources collectées")

if __name__ == "__main__":
    main()
