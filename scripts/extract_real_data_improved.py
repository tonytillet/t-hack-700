#!/usr/bin/env python3
"""
Script amélioré pour extraire les vraies données des fichiers JSON volumineux
et créer un dataset cohérent pour l'IA
"""

import pandas as pd
import numpy as np
import json
import os
import requests
import io
from datetime import datetime
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataExtractor:
    def __init__(self):
        self.base_dir = Path("data")
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Fichiers prioritaires avec des données réelles
        self.priority_files = [
            'vaccination_grippe.json',
            'syndromes_grippaux_spf.json', 
            'urgences.json',
            'sos_medecins_spf.json',
            'ansm_open_medic.json',
            'drees_donnees_hospitalières.json',
            'ansm_depenses_medicaments.json'
        ]
    
    def extract_data_from_url(self, url, format_type, dataset_info):
        """Extrait les données d'une URL CSV/JSON"""
        try:
            logger.info(f"Téléchargement de {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Erreur HTTP {response.status_code} pour {url}")
                return None
            
            if format_type == 'csv':
                # Lire le CSV
                df = pd.read_csv(io.StringIO(response.text))
                logger.info(f"CSV téléchargé: {len(df)} lignes, {len(df.columns)} colonnes")
                
            elif format_type == 'json':
                # Lire le JSON
                json_data = response.json()
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    # Essayer de trouver les données dans le JSON
                    if 'data' in json_data:
                        df = pd.DataFrame(json_data['data'])
                    elif 'results' in json_data:
                        df = pd.DataFrame(json_data['results'])
                    else:
                        df = pd.DataFrame([json_data])
                else:
                    logger.warning(f"Format JSON non reconnu pour {url}")
                    return None
                
                logger.info(f"JSON téléchargé: {len(df)} lignes, {len(df.columns)} colonnes")
            
            else:
                logger.warning(f"Format non supporté: {format_type}")
                return None
            
            if df.empty:
                logger.warning(f"DataFrame vide pour {url}")
                return None
            
            # Ajouter des métadonnées
            df['source_dataset'] = dataset_info.get('title', 'Unknown')
            df['source_organization'] = dataset_info.get('organization', {}).get('name', 'Unknown')
            df['resource_url'] = url
            df['extraction_date'] = datetime.now().isoformat()
            df['file_format'] = format_type
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de {url}: {e}")
            return None
    
    def process_json_file(self, file_path):
        """Traite un fichier JSON et extrait les données réelles"""
        logger.info(f"Traitement de {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        extracted_dataframes = []
        
        if isinstance(data, dict) and 'data' in data:
            for dataset in data['data']:
                if 'resources' in dataset:
                    for resource in dataset['resources']:
                        # Filtrer les ressources intéressantes
                        filesize = resource.get('filesize', 0)
                        if filesize is None:
                            filesize = 0
                        
                        if (resource.get('format') in ['csv', 'json'] and 
                            resource.get('url') and 
                            filesize > 1000):  # Plus de 1KB
                            
                            df = self.extract_data_from_url(
                                resource['url'], 
                                resource['format'],
                                dataset
                            )
                            
                            if df is not None:
                                extracted_dataframes.append(df)
        
        return extracted_dataframes
    
    def extract_all_real_data(self):
        """Extrait toutes les données réelles des fichiers JSON"""
        logger.info("Début de l'extraction des données réelles...")
        
        all_dataframes = []
        data_gouv_dir = self.raw_dir / "data_gouv_fr"
        
        for filename in self.priority_files:
            file_path = data_gouv_dir / filename
            if file_path.exists():
                try:
                    extracted_dfs = self.process_json_file(file_path)
                    all_dataframes.extend(extracted_dfs)
                    logger.info(f"Extrait {len(extracted_dfs)} datasets de {filename}")
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de {filename}: {e}")
        
        logger.info(f"Total de datasets extraits: {len(all_dataframes)}")
        return all_dataframes
    
    def save_extracted_data(self, dataframes):
        """Sauvegarde les données extraites"""
        if not dataframes:
            logger.warning("Aucune donnée à sauvegarder")
            return
        
        # Créer le dossier de sortie
        output_dir = self.processed_dir / "real_data"
        output_dir.mkdir(exist_ok=True)
        
        # Sauvegarder chaque dataset séparément
        for i, df in enumerate(dataframes):
            if not df.empty:
                output_file = output_dir / f'real_data_{i:02d}.parquet'
                df.to_parquet(output_file, index=False)
                logger.info(f"Dataset {i} sauvegardé: {output_file} ({len(df)} lignes)")
        
        # Créer un dataset unifié
        try:
            unified_df = pd.concat(dataframes, ignore_index=True, sort=False)
            unified_file = output_dir / 'unified_real_data.parquet'
            unified_df.to_parquet(unified_file, index=False)
            logger.info(f"Dataset unifié sauvegardé: {unified_file} ({len(unified_df)} lignes)")
            
            # Afficher un résumé
            self.print_data_summary(unified_df)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du dataset unifié: {e}")
    
    def print_data_summary(self, df):
        """Affiche un résumé des données extraites"""
        logger.info("=" * 60)
        logger.info("RÉSUMÉ DES DONNÉES EXTRAITES")
        logger.info("=" * 60)
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Colonnes: {list(df.columns)}")
        logger.info(f"Types: {df.dtypes.to_dict()}")
        
        if 'source_dataset' in df.columns:
            logger.info("Datasets sources:")
            for dataset in df['source_dataset'].unique():
                count = len(df[df['source_dataset'] == dataset])
                logger.info(f"  - {dataset}: {count} lignes")
        
        if 'file_format' in df.columns:
            logger.info("Formats de fichiers:")
            for format_type in df['file_format'].unique():
                count = len(df[df['file_format'] == format_type])
                logger.info(f"  - {format_type}: {count} lignes")
    
    def run(self):
        """Lance l'extraction des données réelles"""
        logger.info("🚀 DÉBUT DE L'EXTRACTION DES DONNÉES RÉELLES")
        logger.info("=" * 60)
        
        # Extraire toutes les données
        dataframes = self.extract_all_real_data()
        
        if not dataframes:
            logger.error("Aucune donnée extraite!")
            return
        
        # Sauvegarder les données
        self.save_extracted_data(dataframes)
        
        logger.info("✅ EXTRACTION TERMINÉE")
        logger.info("=" * 60)

if __name__ == "__main__":
    extractor = RealDataExtractor()
    extractor.run()
