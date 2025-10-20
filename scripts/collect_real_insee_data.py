#!/usr/bin/env python3
"""
Collecte des données réelles INSEE
Population, densité, âge, mobilité
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import time

def collect_population_data():
    """Collecte les données de population par département"""
    print("👥 Collecte des données de population...")
    
    # URL de l'API INSEE pour la population
    url = "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-COMMUNES_2023.csv"
    
    try:
        # Headers pour l'API INSEE
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/insee/population_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/insee/population_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'CODGEO' in df.columns:
            df['departement'] = df['CODGEO'].astype(str).str[:2]
        
        # Agrégation par département
        population_dept = df.groupby('departement').agg({
            'P20_POP': 'sum',  # Population totale
            'P20_POP0014': 'sum',  # 0-14 ans
            'P20_POP1529': 'sum',  # 15-29 ans
            'P20_POP3044': 'sum',  # 30-44 ans
            'P20_POP4559': 'sum',  # 45-59 ans
            'P20_POP6074': 'sum',  # 60-74 ans
            'P20_POP75P': 'sum'    # 75+ ans
        }).reset_index()
        
        # Calcul des pourcentages
        population_dept['pct_0_14'] = (population_dept['P20_POP0014'] / population_dept['P20_POP'] * 100).round(2)
        population_dept['pct_15_29'] = (population_dept['P20_POP1529'] / population_dept['P20_POP'] * 100).round(2)
        population_dept['pct_30_44'] = (population_dept['P20_POP3044'] / population_dept['P20_POP'] * 100).round(2)
        population_dept['pct_45_59'] = (population_dept['P20_POP4559'] / population_dept['P20_POP'] * 100).round(2)
        population_dept['pct_60_74'] = (population_dept['P20_POP6074'] / population_dept['P20_POP'] * 100).round(2)
        population_dept['pct_75_plus'] = (population_dept['P20_POP75P'] / population_dept['P20_POP'] * 100).round(2)
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/insee/insee_population_real_{timestamp}.csv'
        population_dept.to_csv(filename, index=False)
        
        print(f"✅ Données de population collectées: {len(population_dept)} départements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte population: {e}")
        return None

def collect_density_data():
    """Collecte les données de densité de population"""
    print("🏙️ Collecte des données de densité...")
    
    # URL de l'API INSEE pour la densité
    url = "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-DENSITE_2023.csv"
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/insee/density_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/insee/density_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'CODGEO' in df.columns:
            df['departement'] = df['CODGEO'].astype(str).str[:2]
        
        # Agrégation par département
        density_dept = df.groupby('departement').agg({
            'DENSITE': 'mean'  # Densité moyenne
        }).reset_index()
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/insee/insee_density_real_{timestamp}.csv'
        density_dept.to_csv(filename, index=False)
        
        print(f"✅ Données de densité collectées: {len(density_dept)} départements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte densité: {e}")
        return None

def collect_mobility_data():
    """Collecte les données de mobilité (transports)"""
    print("🚌 Collecte des données de mobilité...")
    
    # URL de l'API INSEE pour la mobilité
    url = "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-MOBILITE_2023.csv"
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/insee/mobility_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/insee/mobility_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'CODGEO' in df.columns:
            df['departement'] = df['CODGEO'].astype(str).str[:2]
        
        # Agrégation par département
        mobility_dept = df.groupby('departement').agg({
            'P20_ACTOCC15P': 'sum',  # Actifs occupés
            'P20_ACTOCC15P_CS1': 'sum',  # Agriculteurs
            'P20_ACTOCC15P_CS2': 'sum',  # Artisans, commerçants
            'P20_ACTOCC15P_CS3': 'sum',  # Cadres
            'P20_ACTOCC15P_CS4': 'sum',  # Professions intermédiaires
            'P20_ACTOCC15P_CS5': 'sum',  # Employés
            'P20_ACTOCC15P_CS6': 'sum'   # Ouvriers
        }).reset_index()
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/insee/insee_mobility_real_{timestamp}.csv'
        mobility_dept.to_csv(filename, index=False)
        
        print(f"✅ Données de mobilité collectées: {len(mobility_dept)} départements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte mobilité: {e}")
        return None

def collect_education_data():
    """Collecte les données d'éducation (écoles, universités)"""
    print("🏫 Collecte des données d'éducation...")
    
    # URL de l'API INSEE pour l'éducation
    url = "https://api.insee.fr/donnees-locales/V0.1/donnees/geo-EDUCATION_2023.csv"
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/insee/education_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/insee/education_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'CODGEO' in df.columns:
            df['departement'] = df['CODGEO'].astype(str).str[:2]
        
        # Agrégation par département
        education_dept = df.groupby('departement').agg({
            'P20_SCOL15P': 'sum',  # Scolarisés 15+
            'P20_SCOL15P_3P': 'sum',  # Scolarisés 15+ 3e cycle
            'P20_SCOL15P_2C': 'sum',  # Scolarisés 15+ 2e cycle
            'P20_SCOL15P_1C': 'sum'   # Scolarisés 15+ 1er cycle
        }).reset_index()
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/insee/insee_education_real_{timestamp}.csv'
        education_dept.to_csv(filename, index=False)
        
        print(f"✅ Données d'éducation collectées: {len(education_dept)} départements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte éducation: {e}")
        return None

def main():
    """Fonction principale de collecte"""
    print("🚀 COLLECTE DES DONNÉES RÉELLES INSEE")
    print("=" * 60)
    
    # Création du dossier
    os.makedirs('data/insee', exist_ok=True)
    
    # Collecte des données
    files = []
    
    # 1. Population
    population_file = collect_population_data()
    if population_file:
        files.append(population_file)
    
    time.sleep(2)
    
    # 2. Densité
    density_file = collect_density_data()
    if density_file:
        files.append(density_file)
    
    time.sleep(2)
    
    # 3. Mobilité
    mobility_file = collect_mobility_data()
    if mobility_file:
        files.append(mobility_file)
    
    time.sleep(2)
    
    # 4. Éducation
    education_file = collect_education_data()
    if education_file:
        files.append(education_file)
    
    # Résumé
    print(f"\n✅ COLLECTE TERMINÉE")
    print(f"📁 Fichiers créés: {len(files)}")
    for file in files:
        print(f"  - {file}")
    
    # Sauvegarde de la configuration
    config = {
        'collection_date': datetime.now().isoformat(),
        'files': files,
        'source': 'INSEE',
        'data_type': 'real'
    }
    
    with open('data/insee/collection_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n📋 Configuration sauvegardée: data/insee/collection_config.json")

if __name__ == "__main__":
    main()
