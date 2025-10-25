#!/usr/bin/env python3
"""
Script de test simple pour identifier les problèmes
"""

import pandas as pd
import pyarrow as pa
import json
import os
from pathlib import Path

print('🔍 TEST SIMPLE DU SCRIPT')
print('=' * 40)
print()

# Test 1: Imports
print('✅ TEST 1: IMPORTS')
try:
    import pandas as pd
    import pyarrow as pa
    import json
    import os
    from pathlib import Path
    print('• Tous les imports OK')
except Exception as e:
    print(f'• Erreur imports: {e}')
    exit(1)

# Test 2: Structure des dossiers
print('\n✅ TEST 2: STRUCTURE DES DOSSIERS')
base_dir = Path("data")
raw_dir = base_dir / "raw" / "data_gouv_fr"
processed_dir = base_dir / "processed"

print(f'• Base dir: {base_dir.exists()}')
print(f'• Raw dir: {raw_dir.exists()}')
print(f'• Processed dir: {processed_dir.exists()}')

if not raw_dir.exists():
    print('❌ Dossier data_gouv_fr non trouvé')
    exit(1)

# Test 3: Fichiers JSON
print('\n✅ TEST 3: FICHIERS JSON')
files = [f for f in raw_dir.iterdir() if f.suffix == '.json']
print(f'• Fichiers JSON trouvés: {len(files)}')

if len(files) == 0:
    print('❌ Aucun fichier JSON trouvé')
    exit(1)

# Test 4: Lecture d'un fichier JSON
print('\n✅ TEST 4: LECTURE D\'UN FICHIER JSON')
test_file = files[0]
print(f'• Test avec: {test_file.name}')

try:
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'data' in data:
        print(f'• Datasets: {len(data["data"])}')
        print('• Format JSON OK')
    else:
        print('• Format JSON non reconnu')
        
except Exception as e:
    print(f'• Erreur lecture JSON: {e}')
    exit(1)

# Test 5: Création de dossiers
print('\n✅ TEST 5: CRÉATION DE DOSSIERS')
analyzed_dir = processed_dir / "analyzed_data"

try:
    analyzed_dir.mkdir(exist_ok=True)
    print(f'• Dossier créé: {analyzed_dir}')
except Exception as e:
    print(f'• Erreur création dossier: {e}')
    exit(1)

# Test 6: Test pandas/pyarrow
print('\n✅ TEST 6: PANDAS/PYARROW')
try:
    # Créer un DataFrame de test
    test_df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    # Sauvegarder en Parquet
    test_file = analyzed_dir / 'test.parquet'
    test_df.to_parquet(test_file, index=False)
    
    # Relire le fichier
    df_read = pd.read_parquet(test_file)
    
    print(f'• DataFrame créé: {test_df.shape}')
    print(f'• Parquet sauvegardé: {test_file}')
    print(f'• Parquet relu: {df_read.shape}')
    print('• Pandas/PyArrow OK')
    
except Exception as e:
    print(f'• Erreur pandas/pyarrow: {e}')
    exit(1)

print('\n🎯 TOUS LES TESTS PASSÉS !')
print('Le script devrait fonctionner correctement.')
print()
print('💡 POUR LANCER LE SCRIPT COMPLET:')
print('python3 scripts/analyze_and_clean.py')
