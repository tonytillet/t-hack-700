#!/usr/bin/env python3
"""
Script de nettoyage et standardisation des données LUMEN
Rend les données cohérentes pour la fusion et l'analyse
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import json
import os
from pathlib import Path
from datetime import datetime
import re
import logging

class DataCleaner:
    def __init__(self):
        self.base_dir = Path("data")
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.processed_dir / 'clean_data.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Mapping des régions pour standardisation
        self.region_mapping = {
            'Île-de-France': 'IDF',
            'Auvergne-Rhône-Alpes': 'ARA',
            'Provence-Alpes-Côte d\'Azur': 'PACA',
            'Occitanie': 'OCC',
            'Nouvelle-Aquitaine': 'NAQ',
            'Grand Est': 'GE',
            'Hauts-de-France': 'HDF',
            'Bretagne': 'BRE',
            'Normandie': 'NOR',
            'Pays de la Loire': 'PDL',
            'Centre-Val de Loire': 'CVL',
            'Bourgogne-Franche-Comté': 'BFC',
            'Corse': 'COR'
        }
        
        # Colonnes standardisées
        self.standard_columns = {
            'date': 'date',
            'region': 'region',
            'departement': 'departement',
            'valeur': 'valeur',
            'type_donnee': 'type_donnee',
            'source': 'source',
            'unite': 'unite'
        }
    
    def log(self, message):
        """Log un message"""
        self.logger.info(message)
        print(f"🔧 {message}")
    
    def clean_date(self, date_str):
        """Nettoie et convertit une date en timestamp"""
        if pd.isna(date_str) or date_str == '':
            return None
        
        try:
            # Essayer différents formats de date
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except:
                    continue
            
            # Si aucun format ne fonctionne, essayer pandas auto
            return pd.to_datetime(date_str, errors='coerce')
            
        except:
            return None
    
    def standardize_region(self, region_str):
        """Standardise les noms de régions"""
        if pd.isna(region_str) or region_str == '':
            return 'INCONNU'
        
        region_clean = str(region_str).strip().title()
        
        # Chercher dans le mapping
        for full_name, code in self.region_mapping.items():
            if full_name.lower() in region_clean.lower():
                return code
        
        # Si pas trouvé, retourner le nom nettoyé
        return region_clean
    
    def clean_numeric(self, value):
        """Nettoie une valeur numérique"""
        if pd.isna(value) or value == '':
            return None
        
        try:
            # Nettoyer les espaces et caractères spéciaux
            clean_value = str(value).replace(' ', '').replace(',', '.')
            # Enlever les caractères non numériques sauf le point et le moins
            clean_value = re.sub(r'[^\d.-]', '', clean_value)
            
            if clean_value == '' or clean_value == '-':
                return None
            
            return float(clean_value)
        except:
            return None
    
    def process_data_gouv_fr(self):
        """Traite les données data.gouv.fr"""
        self.log("🦠 Nettoyage des données data.gouv.fr...")
        
        data_gouv_dir = self.raw_dir / "data_gouv_fr"
        if not data_gouv_dir.exists():
            self.log("❌ Dossier data_gouv_fr non trouvé")
            return pd.DataFrame()
        
        all_dataframes = []
        
        for json_file in data_gouv_dir.glob("*.json"):
            try:
                self.log(f"  Traitement: {json_file.name}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraire les données du JSON
                if 'data' in data and isinstance(data['data'], list):
                    df = pd.DataFrame(data['data'])
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    self.log(f"    ⚠️ Format non reconnu: {json_file.name}")
                    continue
                
                if df.empty:
                    self.log(f"    ⚠️ DataFrame vide: {json_file.name}")
                    continue
                
                # Standardiser les colonnes
                df_clean = self.standardize_dataframe(df, json_file.stem, 'data_gouv_fr')
                all_dataframes.append(df_clean)
                
                self.log(f"    ✅ {len(df_clean)} lignes nettoyées")
                
            except Exception as e:
                self.log(f"    ❌ Erreur {json_file.name}: {str(e)}")
        
        if all_dataframes:
            result_df = pd.concat(all_dataframes, ignore_index=True)
            self.log(f"✅ Total data.gouv.fr: {len(result_df)} lignes")
            return result_df
        else:
            self.log("❌ Aucune donnée data.gouv.fr traitée")
            return pd.DataFrame()
    
    def process_weather_data(self):
        """Traite les données météo"""
        self.log("🌦️ Nettoyage des données météo...")
        
        weather_file = self.raw_dir / "other" / "donnees_meteo.json"
        if not weather_file.exists():
            self.log("❌ Fichier météo non trouvé")
            return pd.DataFrame()
        
        try:
            with open(weather_file, 'r', encoding='utf-8') as f:
                weather_data = json.load(f)
            
            all_weather = []
            
            for city, data in weather_data.items():
                if 'current' in data:
                    current = data['current']
                    weather_row = {
                        'date': pd.to_datetime(current.get('time', datetime.now())),
                        'region': self.standardize_region(city),
                        'departement': city,
                        'valeur': current.get('temperature_2m', 0),
                        'type_donnee': 'temperature',
                        'source': 'open_meteo',
                        'unite': 'celsius'
                    }
                    all_weather.append(weather_row)
                
                # Traiter les données horaires si disponibles
                if 'hourly' in data and 'time' in data['hourly']:
                    hourly_df = pd.DataFrame({
                        'time': data['hourly']['time'],
                        'temperature': data['hourly'].get('temperature_2m', []),
                        'humidity': data['hourly'].get('relative_humidity_2m', []),
                        'precipitation': data['hourly'].get('precipitation', [])
                    })
                    
                    for _, row in hourly_df.iterrows():
                        if not pd.isna(row['temperature']):
                            weather_row = {
                                'date': pd.to_datetime(row['time']),
                                'region': self.standardize_region(city),
                                'departement': city,
                                'valeur': row['temperature'],
                                'type_donnee': 'temperature_hourly',
                                'source': 'open_meteo',
                                'unite': 'celsius'
                            }
                            all_weather.append(weather_row)
            
            if all_weather:
                df = pd.DataFrame(all_weather)
                self.log(f"✅ Données météo: {len(df)} lignes")
                return df
            else:
                self.log("❌ Aucune donnée météo valide")
                return pd.DataFrame()
                
        except Exception as e:
            self.log(f"❌ Erreur météo: {str(e)}")
            return pd.DataFrame()
    
    def process_wikipedia_data(self):
        """Traite les données Wikipedia"""
        self.log("🧠 Nettoyage des données Wikipedia...")
        
        wiki_file = self.raw_dir / "other" / "wikipedia_sante.json"
        if not wiki_file.exists():
            self.log("❌ Fichier Wikipedia non trouvé")
            return pd.DataFrame()
        
        try:
            with open(wiki_file, 'r', encoding='utf-8') as f:
                wiki_data = json.load(f)
            
            all_wiki = []
            
            for page_title, page_data in wiki_data.items():
                wiki_row = {
                    'date': datetime.now(),
                    'region': 'FRANCE',
                    'departement': 'NATIONAL',
                    'valeur': len(page_data.get('text', '')),
                    'type_donnee': 'wikipedia_content_length',
                    'source': 'wikipedia',
                    'unite': 'characters'
                }
                all_wiki.append(wiki_row)
                
                # Ajouter une ligne pour le résumé
                wiki_row_summary = {
                    'date': datetime.now(),
                    'region': 'FRANCE',
                    'departement': 'NATIONAL',
                    'valeur': len(page_data.get('summary', '')),
                    'type_donnee': 'wikipedia_summary_length',
                    'source': 'wikipedia',
                    'unite': 'characters'
                }
                all_wiki.append(wiki_row_summary)
            
            if all_wiki:
                df = pd.DataFrame(all_wiki)
                self.log(f"✅ Données Wikipedia: {len(df)} lignes")
                return df
            else:
                self.log("❌ Aucune donnée Wikipedia valide")
                return pd.DataFrame()
                
        except Exception as e:
            self.log(f"❌ Erreur Wikipedia: {str(e)}")
            return pd.DataFrame()
    
    def standardize_dataframe(self, df, data_type, source):
        """Standardise un DataFrame selon le schéma commun"""
        if df.empty:
            return df
        
        # Créer un DataFrame standardisé
        standardized_data = []
        
        for _, row in df.iterrows():
            # Essayer d'extraire les informations importantes
            date_value = None
            region_value = 'FRANCE'
            departement_value = 'NATIONAL'
            valeur_value = None
            unite_value = 'unite'
            
            # Chercher une colonne de date
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                    date_value = self.clean_date(row[col])
                    break
            
            # Chercher une colonne de région/département
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['region', 'departement', 'geo', 'location']):
                    region_value = self.standardize_region(row[col])
                    break
            
            # Chercher une colonne de valeur numérique
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['valeur', 'value', 'count', 'nombre', 'total']):
                    valeur_value = self.clean_numeric(row[col])
                    break
            
            # Si pas de valeur trouvée, essayer les colonnes numériques
            if valeur_value is None:
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]) and not pd.isna(row[col]):
                        valeur_value = self.clean_numeric(row[col])
                        break
            
            # Créer la ligne standardisée
            standardized_row = {
                'date': date_value or datetime.now(),
                'region': region_value,
                'departement': departement_value,
                'valeur': valeur_value or 0,
                'type_donnee': data_type,
                'source': source,
                'unite': unite_value
            }
            
            standardized_data.append(standardized_row)
        
        return pd.DataFrame(standardized_data)
    
    def save_processed_data(self, df, filename):
        """Sauvegarde les données nettoyées en Parquet"""
        if df.empty:
            self.log(f"⚠️ DataFrame vide pour {filename}")
            return
        
        filepath = self.processed_dir / f"{filename}.parquet"
        
        try:
            # Convertir en PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Sauvegarder en Parquet
            pq.write_table(table, filepath)
            
            # Statistiques du fichier
            file_size = filepath.stat().st_size / 1024  # KB
            self.log(f"✅ Sauvegardé: {filename}.parquet ({len(df)} lignes, {file_size:.1f} KB)")
            
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde {filename}: {str(e)}")
    
    def run_cleaning(self):
        """Lance le processus de nettoyage complet"""
        self.log("🚀 DÉBUT DU NETTOYAGE DES DONNÉES LUMEN")
        self.log("=" * 50)
        
        all_clean_data = []
        
        try:
            # 1. Nettoyer data.gouv.fr
            data_gouv_clean = self.process_data_gouv_fr()
            if not data_gouv_clean.empty:
                self.save_processed_data(data_gouv_clean, "data_gouv_fr_clean")
                all_clean_data.append(data_gouv_clean)
            
            # 2. Nettoyer météo
            weather_clean = self.process_weather_data()
            if not weather_clean.empty:
                self.save_processed_data(weather_clean, "weather_clean")
                all_clean_data.append(weather_clean)
            
            # 3. Nettoyer Wikipedia
            wiki_clean = self.process_wikipedia_data()
            if not wiki_clean.empty:
                self.save_processed_data(wiki_clean, "wikipedia_clean")
                all_clean_data.append(wiki_clean)
            
            # 4. Fusionner toutes les données
            if all_clean_data:
                self.log("🔄 Fusion des données nettoyées...")
                merged_df = pd.concat(all_clean_data, ignore_index=True)
                
                # Sauvegarder le dataset fusionné
                self.save_processed_data(merged_df, "lumen_merged_clean")
                
                # Statistiques finales
                self.log("=" * 50)
                self.log("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS")
                self.log(f"📊 Total lignes: {len(merged_df)}")
                self.log(f"📊 Colonnes: {list(merged_df.columns)}")
                self.log(f"📊 Sources: {merged_df['source'].value_counts().to_dict()}")
                self.log(f"📊 Types: {merged_df['type_donnee'].value_counts().to_dict()}")
                
                return merged_df
            else:
                self.log("❌ Aucune donnée nettoyée")
                return pd.DataFrame()
                
        except Exception as e:
            self.log(f"❌ ERREUR CRITIQUE: {str(e)}")
            raise

def main():
    """Point d'entrée principal"""
    print("🧹 LUMEN - Nettoyage des données")
    print("=" * 50)
    
    cleaner = DataCleaner()
    clean_data = cleaner.run_cleaning()
    
    print("\n🎯 NETTOYAGE TERMINÉ")
    print("=" * 50)
    print(f"📁 Données nettoyées dans: data/processed/")
    print(f"📝 Logs disponibles dans: data/processed/clean_data.log")

if __name__ == "__main__":
    main()
