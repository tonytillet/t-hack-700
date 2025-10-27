#!/usr/bin/env python3
"""
Script simple pour analyser les colonnes des chunks de vaccination
"""

import pandas as pd
import json
from pathlib import Path

def analyze_vaccination_columns():
    """Analyse les colonnes des chunks de vaccination"""
    print('🔍 ANALYSE DES COLONNES - VACCINATION GRIPPE')
    print('=' * 60)
    
    # Dossier des chunks
    chunks_dir = Path('data/processed/analyzed_data')
    
    # Trouver tous les chunks de vaccination
    vaccination_chunks = list(chunks_dir.glob('chunk_Vaccination_Grippe_*.parquet'))
    
    print(f'📊 Chunks de vaccination trouvés: {len(vaccination_chunks)}')
    print()
    
    # Analyser chaque chunk
    all_columns = set()
    column_types = {}
    
    for i, chunk_file in enumerate(vaccination_chunks):
        try:
            print(f'📅 CHUNK {i+1}: {chunk_file.name}')
            df = pd.read_parquet(chunk_file)
            
            print(f'   Shape: {df.shape}')
            print(f'   Colonnes: {list(df.columns)}')
            
            # Collecter toutes les colonnes
            all_columns.update(df.columns)
            
            # Collecter les types
            for col, dtype in df.dtypes.items():
                if col not in column_types:
                    column_types[col] = set()
                column_types[col].add(str(dtype))
            
            # Afficher quelques exemples
            print('   Exemples de valeurs:')
            for col in df.columns[:3]:  # Premières 3 colonnes
                unique_vals = df[col].unique()[:2]
                print(f'     - {col}: {unique_vals}')
            
            print('-' * 40)
            
        except Exception as e:
            print(f'❌ Erreur lecture {chunk_file}: {e}')
            print('-' * 40)
    
    # Résumé final
    print('📋 RÉSUMÉ FINAL')
    print('=' * 40)
    print(f'Total colonnes uniques: {len(all_columns)}')
    print(f'Colonnes disponibles: {sorted(all_columns)}')
    print()
    print('Types par colonne:')
    for col in sorted(all_columns):
        types = ', '.join(column_types[col])
        print(f'  - {col}: {types}')

if __name__ == "__main__":
    analyze_vaccination_columns()
