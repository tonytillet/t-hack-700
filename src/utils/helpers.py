#!/usr/bin/env python3
"""
Fonctions utilitaires et helpers pour l'application
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def load_config():
    """Charge la configuration de l'application"""
    config_file = 'config/app_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return get_default_config()

def get_default_config():
    """Retourne la configuration par défaut"""
    return {
        'data_paths': {
            'processed': 'data/processed',
            'alerts': 'data/alerts',
            'spf': 'data/spf',
            'insee': 'data/insee',
            'meteo': 'data/meteo'
        },
        'thresholds': {
            'alert_critical': 80,
            'alert_elevated': 60,
            'alert_moderate': 40
        },
        'regions': [
            'Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur',
            'Nouvelle-Aquitaine', 'Occitanie', 'Grand Est', 'Hauts-de-France',
            'Normandie', 'Bretagne', 'Pays de la Loire', 'Centre-Val de Loire',
            'Bourgogne-Franche-Comté', 'Corse'
        ]
    }

def format_number(value, decimals=1):
    """Formate un nombre avec le bon nombre de décimales"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}"

def format_percentage(value, decimals=1):
    """Formate un pourcentage"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"

def format_currency(value):
    """Formate une valeur monétaire"""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}€"

def get_latest_file(directory, pattern):
    """Retourne le fichier le plus récent correspondant au pattern"""
    if not os.path.exists(directory):
        return None

    files = [f for f in os.listdir(directory) if pattern in f]
    if not files:
        return None

    return sorted(files)[-1]

def calculate_trend(data, column, periods=4):
    """Calcule la tendance sur les dernières périodes"""
    if len(data) < periods:
        return 0

    recent = data[column].tail(periods)
    return (recent.iloc[-1] - recent.iloc[0]) / recent.iloc[0] * 100

def validate_data_integrity(df):
    """Valide l'intégrité des données"""
    issues = []

    # Vérification des valeurs manquantes
    missing_pct = df.isnull().sum() / len(df) * 100
    high_missing = missing_pct[missing_pct > 50]

    if not high_missing.empty:
        issues.append(f"Colonnes avec >50% valeurs manquantes: {list(high_missing.index)}")

    # Vérification des valeurs aberrantes
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].std() > 0:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = (z_scores > 3).sum()
            if outliers > 0:
                issues.append(f"{outliers} valeurs aberrantes détectées dans {col}")

    return issues

def create_backup_filename(original_name, suffix="_backup"):
    """Crée un nom de fichier de sauvegarde"""
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}{suffix}_{timestamp}{ext}"

def ensure_directory(path):
    """Crée un dossier s'il n'existe pas"""
    os.makedirs(path, exist_ok=True)

def get_region_coordinates():
    """Retourne les coordonnées des régions françaises"""
    return {
        'Île-de-France': [48.8566, 2.3522],
        'Auvergne-Rhône-Alpes': [45.7640, 4.8357],
        'Provence-Alpes-Côte d\'Azur': [43.2965, 5.3698],
        'Nouvelle-Aquitaine': [44.8378, -0.5792],
        'Occitanie': [43.6047, 1.4442],
        'Grand Est': [48.5734, 7.7521],
        'Hauts-de-France': [50.6292, 3.0573],
        'Normandie': [49.1829, -0.3707],
        'Bretagne': [48.2020, -2.9326],
        'Pays de la Loire': [47.4739, -0.5517],
        'Centre-Val de Loire': [47.7516, 1.6751],
        'Bourgogne-Franche-Comté': [47.3220, 5.0415],
        'Corse': [42.0396, 9.0129]
    }
