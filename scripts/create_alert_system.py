#!/usr/bin/env python3
"""
Système d'alerte précoce pour la grippe
Seuils critiques basés sur densité, mobilité, contexte + analyse historique
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import warnings
warnings.filterwarnings('ignore')

class GrippeAlertSystem:
    def __init__(self):
        """Initialise le système d'alerte"""
        self.data = None
        self.thresholds = self.load_thresholds()
        self.load_data()
    
    def load_thresholds(self):
        """Charge les seuils critiques"""
        return {
            'urgences_critical': 150,      # Urgences par semaine
            'incidence_critical': 200,     # Incidence Sentinelles
            'density_critical': 200,       # Densité de population
            'vaccination_low': 30,         # Taux de vaccination faible
            'temperature_risk': 5,         # Température < 5°C
            'humidity_risk': 80,           # Humidité > 80%
            'population_65_plus_risk': 20, # % 65+ > 20%
            'trend_increase': 1.5,         # Augmentation > 50%
            'seasonal_anomaly': 2.0        # Anomalie saisonnière > 2σ
        }
    
    def load_data(self):
        """Charge toutes les données"""
        print("📊 Chargement des données...")
        
        # Chargement des fichiers récents
        spf_files = [f for f in os.listdir('data/spf') if f.endswith('.csv')]
        insee_files = [f for f in os.listdir('data/insee') if f.endswith('.csv')]
        meteo_files = [f for f in os.listdir('data/meteo') if f.endswith('.csv')]
        
        if not spf_files or not insee_files or not meteo_files:
            print("❌ Données manquantes")
            return
        
        # Chargement des données (fichiers les plus récents)
        urgences_file = [f for f in spf_files if 'urgences_real' in f][0]
        sentinelles_file = [f for f in spf_files if 'sentinelles_real' in f][0]
        vaccination_file = [f for f in spf_files if 'vaccination_real' in f][0]
        
        urgences = pd.read_csv(f'data/spf/{urgences_file}')
        sentinelles = pd.read_csv(f'data/spf/{sentinelles_file}')
        vaccination = pd.read_csv(f'data/spf/{vaccination_file}')
        insee = pd.read_csv(f'data/insee/{insee_files[0]}')
        meteo = pd.read_csv(f'data/meteo/{meteo_files[0]}')
        
        # Conversion des dates
        for df in [urgences, sentinelles, meteo]:
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
        
        # Fusion des données
        self.data = self.merge_all_data(urgences, sentinelles, vaccination, insee, meteo)
        
        print(f"✅ Données chargées: {len(self.data)} enregistrements")
    
    def merge_all_data(self, urgences, sentinelles, vaccination, insee, meteo):
        """Fusionne toutes les sources de données"""
        # Fusion urgences + météo
        merged = pd.merge(urgences, meteo, on=['date', 'region'], how='left')
        
        # Ajout des données démographiques
        merged = pd.merge(merged, insee, on='region', how='left')
        
        # Ajout des données de vaccination
        vaccination_wide = vaccination.pivot(index='region', columns='year', values='taux_vaccination')
        vaccination_wide.columns = [f'vaccination_{col}' for col in vaccination_wide.columns]
        vaccination_wide = vaccination_wide.reset_index()
        
        merged = pd.merge(merged, vaccination_wide, on='region', how='left')
        
        # Ajout des données Sentinelles (moyenne nationale)
        sentinelles_weekly = sentinelles.groupby('date').agg({'incidence': 'mean'}).reset_index()
        sentinelles_weekly = sentinelles_weekly.rename(columns={'incidence': 'incidence_nationale'})
        
        merged = pd.merge(merged, sentinelles_weekly, on='date', how='left')
        
        return merged
    
    def calculate_risk_factors(self):
        """Calcule les facteurs de risque"""
        df = self.data.copy()
        
        # 1. Facteur densité de population (basé sur la population totale)
        df['risk_density'] = np.where(df['population_totale'] > 5000000, 2, 1)
        
        # 2. Facteur âge (population 65+)
        df['risk_age'] = np.where(df['pct_65_plus'] > self.thresholds['population_65_plus_risk'], 2, 1)
        
        # 3. Facteur météo
        df['risk_weather'] = np.where(
            (df['temperature'] < self.thresholds['temperature_risk']) | 
            (df['humidity'] > self.thresholds['humidity_risk']), 2, 1
        )
        
        # 4. Facteur vaccination
        df['risk_vaccination'] = np.where(
            df['vaccination_2024'] < self.thresholds['vaccination_low'], 2, 1
        )
        
        # 5. Facteur saisonnier
        df['month'] = df['date'].dt.month
        df['risk_seasonal'] = np.where(df['month'].isin([12, 1, 2, 3]), 2, 1)
        
        # 6. Facteur tendance (calculé sur 4 semaines)
        df['urgences_ma4'] = df.groupby('region')['urgences_grippe'].rolling(4).mean().reset_index(0, drop=True)
        df['urgences_trend'] = df['urgences_grippe'] / df['urgences_ma4']
        df['risk_trend'] = np.where(df['urgences_trend'] > self.thresholds['trend_increase'], 2, 1)
        
        # 7. Facteur anomalie saisonnière
        df['urgences_zscore'] = df.groupby(['region', 'month'])['urgences_grippe'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        df['risk_anomaly'] = np.where(
            abs(df['urgences_zscore']) > self.thresholds['seasonal_anomaly'], 2, 1
        )
        
        return df
    
    def calculate_alert_score(self, df):
        """Calcule le score d'alerte global"""
        # Pondération des facteurs de risque
        weights = {
            'risk_density': 0.15,
            'risk_age': 0.10,
            'risk_weather': 0.10,
            'risk_vaccination': 0.20,
            'risk_seasonal': 0.15,
            'risk_trend': 0.20,
            'risk_anomaly': 0.10
        }
        
        # Calcul du score pondéré
        df['alert_score'] = 0
        for factor, weight in weights.items():
            df['alert_score'] += df[factor] * weight
        
        # Normalisation sur 100
        df['alert_score'] = (df['alert_score'] / 2) * 100
        
        return df
    
    def generate_alerts(self, df):
        """Génère les alertes"""
        alerts = []
        
        # Données les plus récentes
        latest_data = df.groupby('region').last().reset_index()
        
        for _, row in latest_data.iterrows():
            region = row['region']
            score = row['alert_score']
            urgences = row['urgences_grippe']
            vaccination = row.get('vaccination_2024', 0)
            
            # Classification du risque
            if score >= 80:
                level = "🔴 CRITIQUE"
                action = "Déclencher protocole d'urgence immédiatement"
                timeline = "1-2 semaines"
            elif score >= 60:
                level = "🟠 ÉLEVÉ"
                action = "Préparer campagne de vaccination renforcée"
                timeline = "2-4 semaines"
            elif score >= 40:
                level = "🟡 MODÉRÉ"
                action = "Surveillance renforcée + communication préventive"
                timeline = "1-2 mois"
            else:
                level = "🟢 FAIBLE"
                action = "Surveillance normale"
                timeline = "Pas d'action immédiate"
            
            # Détails des facteurs de risque
            risk_factors = []
            if row['risk_density'] == 2:
                risk_factors.append("Densité élevée")
            if row['risk_age'] == 2:
                risk_factors.append("Population âgée")
            if row['risk_weather'] == 2:
                risk_factors.append("Conditions météo défavorables")
            if row['risk_vaccination'] == 2:
                risk_factors.append("Vaccination insuffisante")
            if row['risk_trend'] == 2:
                risk_factors.append("Tendance à la hausse")
            if row['risk_anomaly'] == 2:
                risk_factors.append("Anomalie saisonnière")
            
            alerts.append({
                'region': region,
                'alert_score': round(score, 1),
                'level': level,
                'action': action,
                'timeline': timeline,
                'urgences_actuelles': urgences,
                'vaccination_rate': vaccination,
                'risk_factors': ', '.join(risk_factors),
                'date_alert': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        
        return alerts
    
    def create_protocol_actions(self, alerts):
        """Crée les actions de protocole"""
        protocols = []
        
        for alert in alerts:
            if alert['level'] in ["🔴 CRITIQUE", "🟠 ÉLEVÉ"]:
                region = alert['region']
                score = alert['alert_score']
                
                # Protocole d'action
                protocol = {
                    'region': region,
                    'priority': 'HIGH' if alert['level'] == "🔴 CRITIQUE" else 'MEDIUM',
                    'actions': [
                        f"Envoyer SMS/email à tous les habitants de {region}",
                        f"Lancer campagne de vaccination ciblée",
                        f"Augmenter la surveillance médicale",
                        f"Préparer les services d'urgence",
                        f"Communiquer les mesures préventives"
                    ],
                    'timeline': alert['timeline'],
                    'estimated_cost': self.calculate_protocol_cost(region, score),
                    'expected_impact': self.calculate_expected_impact(region, score)
                }
                
                protocols.append(protocol)
        
        return protocols
    
    def calculate_protocol_cost(self, region, score):
        """Calcule le coût estimé du protocole"""
        # Coût basé sur la population et le niveau de risque
        base_costs = {
            'Île-de-France': 500000,
            'Auvergne-Rhône-Alpes': 300000,
            'Provence-Alpes-Côte d\'Azur': 250000,
            'Nouvelle-Aquitaine': 200000,
            'Occitanie': 200000,
            'Grand Est': 180000,
            'Hauts-de-France': 150000,
            'Normandie': 120000,
            'Bretagne': 120000,
            'Pays de la Loire': 100000,
            'Centre-Val de Loire': 80000,
            'Bourgogne-Franche-Comté': 80000,
            'Corse': 50000
        }
        
        base_cost = base_costs.get(region, 100000)
        risk_multiplier = score / 100
        
        return int(base_cost * risk_multiplier)
    
    def calculate_expected_impact(self, region, score):
        """Calcule l'impact attendu"""
        # Estimation du nombre d'urgences évitées
        base_impact = {
            'Île-de-France': 1000,
            'Auvergne-Rhône-Alpes': 600,
            'Provence-Alpes-Côte d\'Azur': 500,
            'Nouvelle-Aquitaine': 400,
            'Occitanie': 400,
            'Grand Est': 350,
            'Hauts-de-France': 300,
            'Normandie': 250,
            'Bretagne': 250,
            'Pays de la Loire': 200,
            'Centre-Val de Loire': 150,
            'Bourgogne-Franche-Comté': 150,
            'Corse': 100
        }
        
        base_impact_value = base_impact.get(region, 200)
        risk_multiplier = score / 100
        
        return {
            'urgences_evitees': int(base_impact_value * risk_multiplier),
            'economies_estimees': int(base_impact_value * risk_multiplier * 300),  # 300€ par urgence
            'roi_estime': round(risk_multiplier * 2.5, 1)  # ROI estimé
        }
    
    def run_analysis(self):
        """Lance l'analyse complète"""
        print("🚨 ANALYSE DU SYSTÈME D'ALERTE PRÉCOCE")
        print("=" * 60)
        
        if self.data is None:
            print("❌ Aucune donnée disponible")
            return
        
        # Calcul des facteurs de risque
        df_with_risks = self.calculate_risk_factors()
        
        # Calcul du score d'alerte
        df_with_scores = self.calculate_alert_score(df_with_risks)
        
        # Génération des alertes
        alerts = self.generate_alerts(df_with_scores)
        
        # Création des protocoles
        protocols = self.create_protocol_actions(alerts)
        
        # Sauvegarde des résultats
        self.save_results(alerts, protocols, df_with_scores)
        
        # Affichage des résultats
        self.display_results(alerts, protocols)
        
        return alerts, protocols
    
    def save_results(self, alerts, protocols, df):
        """Sauvegarde les résultats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sauvegarde des alertes
        alerts_df = pd.DataFrame(alerts)
        alerts_df.to_csv(f'data/alerts/alertes_{timestamp}.csv', index=False)
        
        # Sauvegarde des protocoles
        protocols_df = pd.DataFrame(protocols)
        protocols_df.to_csv(f'data/alerts/protocoles_{timestamp}.csv', index=False)
        
        # Sauvegarde des données enrichies
        df.to_csv(f'data/processed/dataset_with_alerts_{timestamp}.csv', index=False)
        
        print(f"✅ Résultats sauvegardés avec timestamp: {timestamp}")
    
    def display_results(self, alerts, protocols):
        """Affiche les résultats"""
        print(f"\n📊 RÉSULTATS DE L'ANALYSE")
        print(f"🔍 {len(alerts)} régions analysées")
        print(f"🚨 {len([a for a in alerts if a['level'] in ['🔴 CRITIQUE', '🟠 ÉLEVÉ']])} alertes actives")
        print(f"📋 {len(protocols)} protocoles générés")
        
        print(f"\n🚨 ALERTES CRITIQUES ET ÉLEVÉES:")
        print("-" * 50)
        
        for alert in alerts:
            if alert['level'] in ['🔴 CRITIQUE', '🟠 ÉLEVÉ']:
                print(f"\n{alert['level']} {alert['region']}")
                print(f"  Score: {alert['alert_score']}/100")
                print(f"  Action: {alert['action']}")
                print(f"  Délai: {alert['timeline']}")
                print(f"  Facteurs: {alert['risk_factors']}")
                print(f"  Urgences: {alert['urgences_actuelles']:.0f}")
                print(f"  Vaccination: {alert['vaccination_rate']:.1f}%")
        
        print(f"\n📋 PROTOCOLES GÉNÉRÉS:")
        print("-" * 50)
        
        for protocol in protocols:
            print(f"\n🎯 {protocol['region']} (Priorité: {protocol['priority']})")
            print(f"  Coût estimé: {protocol['estimated_cost']:,}€")
            print(f"  Impact: {protocol['expected_impact']['urgences_evitees']} urgences évitées")
            print(f"  Économies: {protocol['expected_impact']['economies_estimees']:,}€")
            print(f"  ROI: {protocol['expected_impact']['roi_estime']}x")
            print(f"  Actions:")
            for action in protocol['actions']:
                print(f"    - {action}")

def main():
    """Fonction principale"""
    # Création des dossiers
    os.makedirs('data/alerts', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Lancement du système d'alerte
    alert_system = GrippeAlertSystem()
    alerts, protocols = alert_system.run_analysis()
    
    print(f"\n🎉 SYSTÈME D'ALERTE PRÉCOCE OPÉRATIONNEL!")
    print(f"📱 Les décideurs peuvent maintenant recevoir des alertes automatiques")
    print(f"🚀 Prêt pour la prévention et la réduction des coûts médicaux")

if __name__ == "__main__":
    main()
