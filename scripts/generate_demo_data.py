#!/usr/bin/env python3
"""
Script pour générer des données de démonstration réalistes
pour le dashboard LUMEN
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
np.random.seed(42)
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 30)
DEPARTMENTS = [f"{i:02d}" for i in range(1, 96)] + ['2A', '2B']

# Paramètres de simulation
BASE_CASES = {
    'low': 30,
    'medium': 60,
    'high': 120
}

def generate_seasonal_pattern(dates):
    """Génère un pattern saisonnier (pic en hiver)"""
    # Convertir en nombre de jours depuis le début
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])

    # Pattern sinusoïdal avec pic en janvier/février (jour 30-60)
    # et creux en été (jour 180-210)
    # Inversé pour avoir le pic en hiver (valeur haute quand sin est bas)
    seasonal = -np.sin((day_of_year - 45) * 2 * np.pi / 365) * 0.5 + 0.5
    return seasonal

def generate_department_data(dept_code, dates):
    """Génère les données pour un département"""

    # Classifier les départements par population (simplifié)
    if dept_code in ['75', '13', '69', '59', '44', '33', '31']:
        base = BASE_CASES['high']  # Grandes villes
        variability = 40
    elif dept_code in ['06', '83', '34', '67', '76', '92', '93', '94']:
        base = BASE_CASES['medium']  # Villes moyennes
        variability = 25
    else:
        base = BASE_CASES['low']  # Zones rurales
        variability = 15

    # Pattern saisonnier
    seasonal = generate_seasonal_pattern(dates)

    # Tendance de base avec variation saisonnière
    trend = base * (0.5 + seasonal)

    # Ajouter du bruit réaliste
    noise = np.random.normal(0, variability * 0.2, len(dates))

    # Ajouter des pics épidémiques occasionnels
    epidemic_peaks = np.zeros(len(dates))
    num_peaks = np.random.randint(2, 5)
    for _ in range(num_peaks):
        peak_center = np.random.randint(0, len(dates))
        peak_width = 14  # 2 semaines
        peak_intensity = np.random.uniform(0.5, 1.5)
        for i in range(max(0, peak_center - peak_width), min(len(dates), peak_center + peak_width)):
            distance = abs(i - peak_center)
            epidemic_peaks[i] += peak_intensity * base * np.exp(-distance / 5)

    # Valeurs réelles (y_target)
    y_target = trend + noise + epidemic_peaks
    y_target = np.maximum(10, y_target)  # Minimum 10 cas

    # Prédictions (légèrement différentes des valeurs réelles)
    prediction_noise = np.random.normal(0, variability * 0.1, len(dates))
    prediction = y_target + prediction_noise
    prediction = np.maximum(10, prediction)

    # Calcul des erreurs
    error = prediction - y_target
    abs_error = np.abs(error)
    relative_error = abs_error / y_target

    # Créer le DataFrame
    df = pd.DataFrame({
        'date': dates,
        'department': dept_code,
        'y_target': y_target,
        'target_date': dates + timedelta(days=7),
        'prediction': prediction,
        'prediction_date': dates,
        'error': error,
        'abs_error': abs_error,
        'relative_error': relative_error
    })

    return df

def main():
    print("🎲 Génération de données de démonstration pour LUMEN")
    print("=" * 60)

    # Générer la liste des dates
    dates = pd.date_range(START_DATE, END_DATE, freq='D')
    print(f"📅 Période: {START_DATE.date()} à {END_DATE.date()}")
    print(f"📊 {len(dates)} jours × {len(DEPARTMENTS)} départements")

    # Générer les données pour chaque département
    all_data = []
    for i, dept in enumerate(DEPARTMENTS, 1):
        df_dept = generate_department_data(dept, dates)
        all_data.append(df_dept)

        if i % 10 == 0:
            print(f"✅ {i}/{len(DEPARTMENTS)} départements générés...")

    # Combiner toutes les données
    df_final = pd.concat(all_data, ignore_index=True)

    print(f"\n📦 Total: {len(df_final):,} lignes générées")
    print(f"📈 Statistiques:")
    print(f"  - y_target: {df_final['y_target'].min():.1f} - {df_final['y_target'].max():.1f}")
    print(f"  - prediction: {df_final['prediction'].min():.1f} - {df_final['prediction'].max():.1f}")
    print(f"  - MAE moyenne: {df_final['abs_error'].mean():.2f}")

    # Sauvegarder
    output_path = Path('data/predictions/predictions.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(output_path, index=False)

    print(f"\n✅ Données sauvegardées: {output_path}")
    print("🚀 Vous pouvez maintenant relancer le dashboard!")

if __name__ == '__main__':
    main()
