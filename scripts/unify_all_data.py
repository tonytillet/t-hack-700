#!/usr/bin/env python3
"""
Script pour unifier toutes les données par chunks et créer le dataset final complet
"""

import pandas as pd
import json
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataUnifier:
    def __init__(self):
        self.base_dir = Path("data")
        self.processed_dir = self.base_dir / "processed"
        self.external_dir = self.processed_dir / "external_data"
        self.output_dir = self.processed_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def load_vaccination_data(self):
        """Charge les données de vaccination"""
        logger.info("📊 CHARGEMENT DES DONNÉES DE VACCINATION")
        logger.info("=" * 40)
        
        try:
            vaccination_file = self.processed_dir / "lumen_final_dataset.parquet"
            df = pd.read_parquet(vaccination_file)
            
            logger.info(f"✅ Vaccination: {df.shape}")
            logger.info(f"   Colonnes: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur vaccination: {e}")
            return None
    
    def load_demographic_data(self):
        """Charge les données démographiques"""
        logger.info("👥 CHARGEMENT DES DONNÉES DÉMOGRAPHIQUES")
        logger.info("=" * 40)
        
        try:
            demo_file = self.external_dir / "demographic_data.parquet"
            df = pd.read_parquet(demo_file)
            
            logger.info(f"✅ Démographie: {df.shape}")
            logger.info(f"   Colonnes: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur démographie: {e}")
            return None
    
    def load_behavioral_data(self):
        """Charge les données comportementales"""
        logger.info("🧠 CHARGEMENT DES DONNÉES COMPORTEMENTALES")
        logger.info("=" * 40)
        
        try:
            behavior_file = self.external_dir / "behavioral_data.parquet"
            df = pd.read_parquet(behavior_file)
            
            logger.info(f"✅ Comportement: {df.shape}")
            logger.info(f"   Colonnes: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur comportement: {e}")
            return None
    
    def load_weather_data(self):
        """Charge les données météo par chunks"""
        logger.info("🌦️ CHARGEMENT DES DONNÉES MÉTÉO")
        logger.info("=" * 40)
        
        try:
            weather_file = self.external_dir / "weather_data_gouv.parquet"
            
            # Lire par chunks pour éviter les problèmes de mémoire
            chunk_size = 50000  # 50k lignes par chunk
            weather_chunks = []
            
            logger.info(f"📁 Lecture par chunks de {chunk_size} lignes...")
            
            for i, chunk in enumerate(pd.read_parquet(weather_file, chunksize=chunk_size)):
                logger.info(f"   Chunk {i+1}: {len(chunk)} lignes")
                
                # Nettoyage basique du chunk
                chunk = self.clean_weather_chunk(chunk)
                
                if not chunk.empty:
                    weather_chunks.append(chunk)
            
            if weather_chunks:
                # Unifier les chunks météo
                weather_df = pd.concat(weather_chunks, ignore_index=True, sort=False)
                logger.info(f"✅ Météo unifiée: {weather_df.shape}")
                return weather_df
            else:
                logger.warning("⚠️ Aucun chunk météo valide")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur météo: {e}")
            return None
    
    def clean_weather_chunk(self, chunk):
        """Nettoie un chunk de données météo"""
        try:
            # Garder seulement les colonnes utiles
            useful_cols = []
            for col in chunk.columns:
                if any(keyword in col.lower() for keyword in ['temp', 'temperature', 'date', 'region', 'ville', 'city']):
                    useful_cols.append(col)
            
            if useful_cols:
                chunk = chunk[useful_cols]
            
            # Supprimer les lignes avec trop de NaN
            chunk = chunk.dropna(thresh=len(chunk.columns) * 0.5)
            
            return chunk
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur nettoyage chunk météo: {e}")
            return pd.DataFrame()
    
    def create_features(self, vaccination_df, demographic_df, behavioral_df, weather_df):
        """Crée des features engineering pour l'IA"""
        logger.info("🔧 CRÉATION DES FEATURES")
        logger.info("=" * 40)
        
        try:
            # Commencer avec les données de vaccination
            final_df = vaccination_df.copy()
            
            # Ajouter les features démographiques
            if demographic_df is not None:
                logger.info("👥 Ajout des features démographiques...")
                
                # Mapper les régions
                region_mapping = {}
                for _, row in demographic_df.iterrows():
                    region_mapping[row['region']] = {
                        'population': row['population'],
                        'density': row['density']
                    }
                
                # Ajouter les features démographiques
                final_df['population'] = final_df['region'].map(lambda x: region_mapping.get(x, {}).get('population', 0))
                final_df['density'] = final_df['region'].map(lambda x: region_mapping.get(x, {}).get('density', 0))
            
            # Ajouter les features comportementales
            if behavioral_df is not None:
                logger.info("🧠 Ajout des features comportementales...")
                
                # Calculer un score comportemental basé sur la longueur des textes
                total_text_length = behavioral_df['text_length'].sum()
                final_df['behavioral_score'] = total_text_length / len(behavioral_df) if len(behavioral_df) > 0 else 0
            
            # Ajouter les features météo (échantillonnage)
            if weather_df is not None:
                logger.info("🌦️ Ajout des features météo...")
                
                # Prendre un échantillon des données météo pour éviter la surcharge
                weather_sample = weather_df.sample(n=min(1000, len(weather_df)), random_state=42)
                
                # Ajouter des features météo moyennes
                if 'temp' in str(weather_sample.columns).lower():
                    temp_cols = [col for col in weather_sample.columns if 'temp' in col.lower()]
                    if temp_cols:
                        final_df['avg_temperature'] = weather_sample[temp_cols[0]].mean() if len(temp_cols) > 0 else 20
                else:
                    final_df['avg_temperature'] = 20  # Température par défaut
            
            # Créer des features temporelles
            logger.info("📅 Création des features temporelles...")
            
            # Features saisonnières
            final_df['season'] = 'unknown'
            if 'campagne' in final_df.columns:
                final_df['season'] = final_df['campagne'].apply(self.get_season)
            
            # Features géographiques
            if 'region' in final_df.columns:
                final_df['region_code'] = final_df['region'].str.extract(r'(\d+)').astype(float)
            
            # Features de groupe d'âge
            if 'groupe' in final_df.columns:
                final_df['age_group'] = final_df['groupe'].apply(self.get_age_group_code)
            
            logger.info(f"✅ Features créées: {final_df.shape}")
            return final_df
            
        except Exception as e:
            logger.error(f"❌ Erreur création features: {e}")
            return vaccination_df
    
    def get_season(self, campagne):
        """Détermine la saison basée sur la campagne"""
        if pd.isna(campagne):
            return 'unknown'
        
        campagne_str = str(campagne)
        if '2021' in campagne_str or '2022' in campagne_str:
            return 'winter'
        elif '2023' in campagne_str:
            return 'spring'
        elif '2024' in campagne_str:
            return 'summer'
        elif '2025' in campagne_str:
            return 'autumn'
        else:
            return 'unknown'
    
    def get_age_group_code(self, groupe):
        """Convertit le groupe d'âge en code numérique"""
        if pd.isna(groupe):
            return 0
        
        groupe_str = str(groupe).lower()
        if 'moins de 65' in groupe_str:
            return 1
        elif '65 ans' in groupe_str:
            return 2
        else:
            return 0
    
    def save_final_dataset(self, final_df):
        """Sauvegarde le dataset final"""
        logger.info("💾 SAUVEGARDE DU DATASET FINAL")
        logger.info("=" * 40)
        
        try:
            # Sauvegarder le dataset complet
            final_file = self.output_dir / "lumen_complete_dataset.parquet"
            final_df.to_parquet(final_file, index=False)
            logger.info(f"✅ Dataset complet sauvegardé: {final_file}")
            
            # Créer un résumé
            summary = {
                "total_rows": len(final_df),
                "total_columns": len(final_df.columns),
                "columns": list(final_df.columns),
                "target_variable": "valeur",
                "features": {
                    "temporal": ["season", "campagne"],
                    "geographic": ["region", "region_code", "population", "density"],
                    "demographic": ["age_group", "groupe"],
                    "behavioral": ["behavioral_score"],
                    "weather": ["avg_temperature"],
                    "target": ["valeur"]
                },
                "creation_date": datetime.now().isoformat()
            }
            
            summary_file = self.output_dir / "dataset_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 Résumé sauvegardé: {summary_file}")
            
            # Afficher les statistiques
            self.print_dataset_stats(final_df)
            
            return final_df
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return None
    
    def print_dataset_stats(self, df):
        """Affiche les statistiques du dataset final"""
        logger.info("📊 STATISTIQUES DU DATASET FINAL")
        logger.info("=" * 50)
        logger.info(f"📊 Shape: {df.shape}")
        logger.info(f"📅 Colonnes: {list(df.columns)}")
        
        # Statistiques par source
        if 'source_file' in df.columns:
            logger.info("📁 Par source:")
            for source in df['source_file'].unique():
                count = len(df[df['source_file'] == source])
                logger.info(f"  - {source}: {count:,} lignes")
        
        # Statistiques par région
        if 'region' in df.columns:
            logger.info("🗺️ Par région:")
            for region in df['region'].unique()[:5]:  # Top 5
                count = len(df[df['region'] == region])
                logger.info(f"  - {region}: {count:,} lignes")
        
        # Statistiques de la target variable
        if 'valeur' in df.columns:
            logger.info("🎯 Target variable (valeur):")
            logger.info(f"  - Moyenne: {df['valeur'].mean():.2f}")
            logger.info(f"  - Médiane: {df['valeur'].median():.2f}")
            logger.info(f"  - Min: {df['valeur'].min():.2f}")
            logger.info(f"  - Max: {df['valeur'].max():.2f}")
        
        logger.info("=" * 50)
    
    def run_unification(self):
        """Lance l'unification complète des données"""
        logger.info("🚀 DÉBUT DE L'UNIFICATION DES DONNÉES")
        logger.info("=" * 60)
        
        # Charger toutes les données
        vaccination_df = self.load_vaccination_data()
        demographic_df = self.load_demographic_data()
        behavioral_df = self.load_behavioral_data()
        weather_df = self.load_weather_data()
        
        if vaccination_df is None:
            logger.error("❌ Impossible de continuer sans données de vaccination")
            return None
        
        # Créer les features
        final_df = self.create_features(vaccination_df, demographic_df, behavioral_df, weather_df)
        
        # Sauvegarder le dataset final
        result = self.save_final_dataset(final_df)
        
        logger.info("✅ UNIFICATION TERMINÉE")
        logger.info("=" * 60)
        
        return result

if __name__ == "__main__":
    unifier = DataUnifier()
    unifier.run_unification()
