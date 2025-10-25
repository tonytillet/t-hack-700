#!/usr/bin/env python3
"""
Script pour extraire les vraies données des fichiers JSON volumineux
et créer un dataset cohérent pour l'IA
"""

import json
import os
import pandas as pd
import requests
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_data_from_json(file_path):
    """Extrait les données réelles d'un fichier JSON de data.gouv.fr"""
    logger.info(f"Traitement du fichier: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    extracted_data = []
    
    if isinstance(data, dict) and 'data' in data:
        for dataset in data['data']:
            if 'resources' in dataset:
                for resource in dataset['resources']:
                    if resource.get('format') in ['csv', 'json'] and resource.get('url'):
                        try:
                            # Télécharger les données réelles
                            response = requests.get(resource['url'], timeout=30)
                            if response.status_code == 200:
                                if resource['format'] == 'csv':
                                    # Lire le CSV
                                    import io
                                    df = pd.read_csv(io.StringIO(response.text))
                                    logger.info(f"CSV téléchargé: {len(df)} lignes, {len(df.columns)} colonnes")
                                    
                                    # Ajouter des métadonnées
                                    df['source_dataset'] = dataset.get('title', 'Unknown')
                                    df['source_organization'] = dataset.get('organization', {}).get('name', 'Unknown')
                                    df['resource_url'] = resource['url']
                                    df['extraction_date'] = datetime.now().isoformat()
                                    
                                    extracted_data.append(df)
                                    
                                elif resource['format'] == 'json':
                                    # Lire le JSON
                                    json_data = response.json()
                                    if isinstance(json_data, list):
                                        df = pd.DataFrame(json_data)
                                        logger.info(f"JSON téléchargé: {len(df)} lignes, {len(df.columns)} colonnes")
                                        
                                        # Ajouter des métadonnées
                                        df['source_dataset'] = dataset.get('title', 'Unknown')
                                        df['source_organization'] = dataset.get('organization', {}).get('name', 'Unknown')
                                        df['resource_url'] = resource['url']
                                        df['extraction_date'] = datetime.now().isoformat()
                                        
                                        extracted_data.append(df)
                                    
                        except Exception as e:
                            logger.warning(f"Erreur lors du téléchargement de {resource['url']}: {e}")
                            continue
    
    return extracted_data

def process_all_data_files():
    """Traite tous les fichiers JSON et extrait les données réelles"""
    data_gouv_dir = 'data/raw/data_gouv_fr/'
    all_dataframes = []
    
    # Traiter les fichiers volumineux (données réelles)
    large_files = [
        'vaccination_grippe.json',
        'syndromes_grippaux_spf.json',
        'urgences.json',
        'sos_medecins_spf.json',
        'ansm_open_medic.json',
        'drees_donnees_hospitalières.json',
        'ansm_depenses_medicaments.json'
    ]
    
    for filename in large_files:
        file_path = os.path.join(data_gouv_dir, filename)
        if os.path.exists(file_path):
            logger.info(f"Traitement de {filename}")
            try:
                extracted_data = extract_data_from_json(file_path)
                all_dataframes.extend(extracted_data)
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {filename}: {e}")
    
    return all_dataframes

def create_clean_dataset():
    """Crée un dataset propre à partir des données extraites"""
    logger.info("Début de l'extraction des données réelles...")
    
    # Extraire toutes les données
    all_dataframes = process_all_data_files()
    
    if not all_dataframes:
        logger.warning("Aucune donnée extraite!")
        return None
    
    logger.info(f"Nombre de datasets extraits: {len(all_dataframes)}")
    
    # Sauvegarder chaque dataset séparément
    output_dir = 'data/processed/real_data/'
    os.makedirs(output_dir, exist_ok=True)
    
    for i, df in enumerate(all_dataframes):
        if not df.empty:
            output_file = os.path.join(output_dir, f'real_data_{i:02d}.parquet')
            df.to_parquet(output_file, index=False)
            logger.info(f"Dataset {i} sauvegardé: {output_file} ({len(df)} lignes)")
    
    # Créer un dataset unifié
    if len(all_dataframes) > 1:
        try:
            # Essayer de concaténer les datasets
            unified_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
            unified_file = os.path.join(output_dir, 'unified_real_data.parquet')
            unified_df.to_parquet(unified_file, index=False)
            logger.info(f"Dataset unifié sauvegardé: {unified_file} ({len(unified_df)} lignes)")
        except Exception as e:
            logger.error(f"Erreur lors de la création du dataset unifié: {e}")
    
    return all_dataframes

if __name__ == "__main__":
    create_clean_dataset()
