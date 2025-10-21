#!/usr/bin/env python3
"""
Script pour générer des données de démonstration pour LUMEN
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import json

def create_demo_data():
    """Crée des données de démonstration complètes"""
    
    # Créer les dossiers nécessaires
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/alerts', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Régions françaises
    regions = [
        'Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur',
        'Nouvelle-Aquitaine', 'Occitanie', 'Grand Est', 'Hauts-de-France',
        'Normandie', 'Bretagne', 'Pays de la Loire', 'Centre-Val de Loire',
        'Bourgogne-Franche-Comté', 'Corse'
    ]
    
    # Générer des données pour les 30 derniers jours
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    # Créer le dataset principal
    data = []
    for date in dates:
        for region in regions:
            # Données simulées avec saisonnalité
            base_urgences = np.random.poisson(50)
            base_vaccination = np.random.normal(65, 10)
            base_ias = np.random.exponential(2)
            
            # Ajouter de la saisonnalité (hiver = plus de grippe)
            month = datetime.strptime(date, '%Y-%m-%d').month
            if month in [12, 1, 2, 3]:  # Hiver
                seasonal_factor = 1.5
            else:
                seasonal_factor = 0.7
            
            urgences = max(0, int(base_urgences * seasonal_factor))
            vaccination = max(0, min(100, base_vaccination))
            ias = max(0, base_ias * seasonal_factor)
            
            # Population simulée
            population = np.random.randint(500000, 12000000)
            
            # Population 65+ (estimation réaliste : 15-25%)
            pct_65_plus = np.random.uniform(15, 25)
            
            # Calculer le score d'alerte
            alert_score = min(100, max(0, 
                (100 - vaccination) * 0.4 + 
                (urgences / 100) * 0.3 + 
                (ias * 10) * 0.3
            ))
            
            data.append({
                'date': date,
                'region': region,
                'urgences_grippe': urgences,
                'vaccination_2024': vaccination,
                'ias_syndrome_grippal': ias,
                'population_totale': population,
                'pct_65_plus': pct_65_plus,
                'alert_score': alert_score,
                'flurisk': alert_score,
                'pred_urgences_grippe_j7': int(urgences * 1.1),
                'pred_urgences_grippe_j14': int(urgences * 1.2),
                'pred_urgences_grippe_j21': int(urgences * 1.3),
                'pred_urgences_grippe_j28': int(urgences * 1.4)
            })
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    # Sauvegarder le dataset principal
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dataset_file = f'data/processed/dataset_with_alerts_{timestamp}.csv'
    df.to_csv(dataset_file, index=False)
    
    # Créer les alertes (seulement pour les régions avec score > 60)
    alerts_data = []
    for region in regions:
        latest_data = df[df['region'] == region].iloc[-1]
        if latest_data['alert_score'] > 60:
            level = 'CRITIQUE' if latest_data['alert_score'] > 80 else 'ÉLEVÉ'
            alerts_data.append({
                'region': region,
                'level': level,
                'alert_score': latest_data['alert_score'],
                'action': 'Action immédiate' if level == 'CRITIQUE' else 'Préparer campagne',
                'timeline': '1-2 semaines',
                'urgences_actuelles': latest_data['urgences_grippe'],
                'vaccination_rate': latest_data['vaccination_2024']
            })
    
    # Si aucune alerte, créer au moins une alerte de démonstration
    if not alerts_data:
        alerts_data = [{
            'region': 'Île-de-France',
            'level': 'ÉLEVÉ',
            'alert_score': 72.5,
            'action': 'Préparer campagne',
            'timeline': '1-2 semaines',
            'urgences_actuelles': 85,
            'vaccination_rate': 52.3
        }]
    
    # Sauvegarder les alertes
    alerts_df = pd.DataFrame(alerts_data)
    alerts_file = f'data/alerts/alertes_{timestamp}.csv'
    alerts_df.to_csv(alerts_file, index=False)
    
    # Créer les protocoles
    protocols_data = []
    for _, alert in alerts_df.iterrows():
        protocols_data.append({
            'region': alert['region'],
            'protocol': f"Campagne de vaccination ciblée - {alert['region']}",
            'estimated_cost': np.random.randint(50000, 200000),
            'expected_roi': np.random.uniform(2.0, 5.0),
            'timeline': alert['timeline']
        })
    
    protocols_df = pd.DataFrame(protocols_data)
    protocols_file = f'data/alerts/protocoles_{timestamp}.csv'
    protocols_df.to_csv(protocols_file, index=False)
    
    # Créer une configuration de modèle simple
    config = {
        'model_type': 'RandomForest',
        'features': ['urgences_grippe', 'vaccination_2024', 'ias_syndrome_grippal', 'population_totale'],
        'targets': ['pred_urgences_grippe_j7', 'pred_urgences_grippe_j14', 'pred_urgences_grippe_j21', 'pred_urgences_grippe_j28'],
        'metrics': {
            'mae_j7': 12.5,
            'mae_j14': 15.2,
            'mae_j21': 18.7,
            'mae_j28': 22.1,
            'r2_j7': 0.78,
            'r2_j14': 0.72,
            'r2_j21': 0.68,
            'r2_j28': 0.63
        }
    }
    
    config_file = f'models/config_{timestamp}.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Données de démonstration générées :")
    print(f"   📊 Dataset: {dataset_file}")
    print(f"   🚨 Alertes: {alerts_file} ({len(alerts_data)} alertes)")
    print(f"   📋 Protocoles: {protocols_file}")
    print(f"   ⚙️  Configuration: {config_file}")
    
    return dataset_file, alerts_file, protocols_file, config_file

if __name__ == "__main__":
    create_demo_data()
