#!/usr/bin/env python3
"""
Script pour créer le dataset final unifié à partir des chunks
"""

import pandas as pd
import json
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_final_dataset():
    """Crée le dataset final unifié"""
    logger.info("🚀 CRÉATION DU DATASET FINAL")
    logger.info("=" * 50)
    
    # Dossier des chunks
    chunks_dir = Path('data/processed/analyzed_data')
    output_dir = Path('data/processed')
    output_dir.mkdir(exist_ok=True)
    
    # Lire l'index des chunks
    index_file = chunks_dir / 'chunks_index.json'
    with open(index_file, 'r') as f:
        chunks = json.load(f)
    
    logger.info(f"📊 Chunks à traiter: {len(chunks)}")
    
    # Collecter tous les DataFrames
    all_dataframes = []
    
    for i, chunk_info in enumerate(chunks):
        try:
            chunk_file = Path(chunk_info['file'])
            logger.info(f"📁 Traitement {i+1}/{len(chunks)}: {chunk_file.name}")
            
            # Lire le chunk
            df = pd.read_parquet(chunk_file)
            
            # Nettoyage basique
            df = df.dropna(subset=['valeur'])  # Garder seulement les lignes avec des valeurs
            
            if not df.empty:
                all_dataframes.append(df)
                logger.info(f"   ✅ Ajouté: {len(df)} lignes")
            else:
                logger.warning(f"   ⚠️ Chunk vide après nettoyage")
                
        except Exception as e:
            logger.error(f"   ❌ Erreur: {e}")
    
    if not all_dataframes:
        logger.error("❌ Aucun DataFrame valide trouvé")
        return
    
    # Unifier tous les DataFrames
    logger.info("🔄 Unification des DataFrames...")
    try:
        unified_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        logger.info(f"✅ Dataset unifié créé: {unified_df.shape}")
        
        # Sauvegarder le dataset final
        output_file = output_dir / 'lumen_final_dataset.parquet'
        unified_df.to_parquet(output_file, index=False)
        logger.info(f"💾 Dataset sauvegardé: {output_file}")
        
        # Afficher un résumé
        print_summary(unified_df)
        
        return unified_df
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'unification: {e}")
        return None

def print_summary(df):
    """Affiche un résumé du dataset final"""
    logger.info("📋 RÉSUMÉ DU DATASET FINAL")
    logger.info("=" * 40)
    logger.info(f"📊 Shape: {df.shape}")
    logger.info(f"📅 Colonnes: {list(df.columns)}")
    
    # Statistiques par source
    if 'source_file' in df.columns:
        logger.info("📁 Par source:")
        for source in df['source_file'].unique():
            count = len(df[df['source_file'] == source])
            logger.info(f"  - {source}: {count:,} lignes")
    
    # Statistiques par variable
    if 'variable' in df.columns:
        logger.info("🎯 Par variable:")
        for var in df['variable'].unique():
            count = len(df[df['variable'] == var])
            logger.info(f"  - {var}: {count:,} lignes")
    
    # Statistiques par région
    if 'region' in df.columns:
        logger.info("🗺️ Par région:")
        for region in df['region'].unique()[:5]:  # Top 5
            count = len(df[df['region'] == region])
            logger.info(f"  - {region}: {count:,} lignes")
    
    logger.info("=" * 40)

if __name__ == "__main__":
    create_final_dataset()
