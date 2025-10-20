#!/usr/bin/env python3
"""
Collecte des données réelles de Santé Publique France
Données officielles de grippe, urgences, vaccination, sentinelles
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
import json

def collect_urgences_data():
    """Collecte les données d'urgences grippe de SPF"""
    print("🏥 Collecte des données d'urgences grippe...")
    
    # URL de l'API SPF pour les urgences grippe
    url = "https://odisse.santepubliquefrance.fr/explore/dataset/grippe-passages-aux-urgences-et-actes-sos-medecins-france/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    
    try:
        # Téléchargement des données
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/spf/urgences_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/spf/urgences_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Filtrage pour la grippe
        if 'sursaud_cl_age_gene' in df.columns:
            df = df[df['sursaud_cl_age_gene'] == 'Tous âges']
        
        if 'sursaud_cl_type_etablissement' in df.columns:
            df = df[df['sursaud_cl_type_etablissement'] == 'urgences']
        
        # Agrégation par semaine et région
        df['week'] = df['date'].dt.isocalendar().week
        df['year'] = df['date'].dt.year
        
        # Groupement par région et semaine
        urgences_weekly = df.groupby(['reg', 'year', 'week']).agg({
            'nbre_pass_corona': 'sum',
            'nbre_pass_tot': 'sum'
        }).reset_index()
        
        # Calcul du pourcentage de grippe
        urgences_weekly['pct_grippe'] = (urgences_weekly['nbre_pass_corona'] / urgences_weekly['nbre_pass_tot'] * 100).fillna(0)
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/spf/spf_urgences_real_{timestamp}.csv'
        urgences_weekly.to_csv(filename, index=False)
        
        print(f"✅ Données d'urgences collectées: {len(urgences_weekly)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte urgences: {e}")
        return None

def collect_sentinelles_data():
    """Collecte les données du réseau Sentinelles"""
    print("🔬 Collecte des données Sentinelles...")
    
    # URL de l'API Sentinelles
    url = "https://www.sentiweb.fr/api/incidence?disease=1&start=2019-01-01&end=2025-12-31"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Conversion en DataFrame
        df = pd.DataFrame(data)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/spf/spf_sentinelles_real_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Données Sentinelles collectées: {len(df)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte Sentinelles: {e}")
        return None

def collect_vaccination_data():
    """Collecte les données de vaccination"""
    print("💉 Collecte des données de vaccination...")
    
    # URL de l'API SPF pour la vaccination
    url = "https://odisse.santepubliquefrance.fr/explore/dataset/couverture-vaccinale-grippe-saisonniere/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/spf/vaccination_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/spf/vaccination_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'annee' in df.columns:
            df['year'] = df['annee']
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/spf/spf_vaccination_real_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Données de vaccination collectées: {len(df)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte vaccination: {e}")
        return None

def collect_ias_data():
    """Collecte les données IAS (Indicateur Avancé Sanitaire)"""
    print("📊 Collecte des données IAS...")
    
    # URL de l'API SPF pour l'IAS
    url = "https://odisse.santepubliquefrance.fr/explore/dataset/indicateur-avance-sanitaire/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarde du fichier brut
        with open('data/spf/ias_raw.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lecture et traitement
        df = pd.read_csv('data/spf/ias_raw.csv', sep=';')
        
        # Nettoyage des données
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/spf/spf_ias_real_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"✅ Données IAS collectées: {len(df)} enregistrements")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur collecte IAS: {e}")
        return None

def main():
    """Fonction principale de collecte"""
    print("🚀 COLLECTE DES DONNÉES RÉELLES SANTÉ PUBLIQUE FRANCE")
    print("=" * 60)
    
    # Création du dossier
    os.makedirs('data/spf', exist_ok=True)
    
    # Collecte des données
    files = []
    
    # 1. Urgences
    urgences_file = collect_urgences_data()
    if urgences_file:
        files.append(urgences_file)
    
    time.sleep(2)  # Pause entre les requêtes
    
    # 2. Sentinelles
    sentinelles_file = collect_sentinelles_data()
    if sentinelles_file:
        files.append(sentinelles_file)
    
    time.sleep(2)
    
    # 3. Vaccination
    vaccination_file = collect_vaccination_data()
    if vaccination_file:
        files.append(vaccination_file)
    
    time.sleep(2)
    
    # 4. IAS
    ias_file = collect_ias_data()
    if ias_file:
        files.append(ias_file)
    
    # Résumé
    print(f"\n✅ COLLECTE TERMINÉE")
    print(f"📁 Fichiers créés: {len(files)}")
    for file in files:
        print(f"  - {file}")
    
    # Sauvegarde de la configuration
    config = {
        'collection_date': datetime.now().isoformat(),
        'files': files,
        'source': 'Santé Publique France',
        'data_type': 'real'
    }
    
    with open('data/spf/collection_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n📋 Configuration sauvegardée: data/spf/collection_config.json")

if __name__ == "__main__":
    main()
