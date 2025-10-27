#!/usr/bin/env python3
"""
Script pour analyser fichier par fichier et créer le clean parquet final
Utilise pandas et pyarrow pour le traitement des données
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import json
import os
import requests
import io
from datetime import datetime
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self):
        self.base_dir = Path("data")
        self.raw_dir = self.base_dir / "raw" / "data_gouv_fr"
        self.processed_dir = self.base_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Dossier pour les données analysées
        self.analyzed_dir = self.processed_dir / "analyzed_data"
        self.analyzed_dir.mkdir(exist_ok=True)
    
    def analyze_json_file(self, file_path):
        """Analyse un fichier JSON et extrait les données"""
        logger.info(f"Analyse de {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or 'data' not in data:
                logger.warning(f"Format non reconnu pour {file_path}")
                return None
            
            analysis = {
                'file': file_path.name,
                'datasets': len(data['data']),
                'total_resources': 0,
                'csv_resources': 0,
                'json_resources': 0,
                'grippe_datasets': [],
                'extracted_data': []
            }
            
            # Analyser chaque dataset
            for dataset in data['data']:
                title = dataset.get('title', '').lower()
                desc = dataset.get('description', '').lower()
                
                # Chercher des données de grippe
                if 'grippe' in title or 'grippe' in desc or 'syndrome' in title or 'syndrome' in desc:
                    analysis['grippe_datasets'].append(dataset.get('title', 'N/A'))
                
                # Analyser les ressources
                if 'resources' in dataset:
                    for resource in dataset['resources']:
                        analysis['total_resources'] += 1
                        
                        if resource.get('format') == 'csv':
                            analysis['csv_resources'] += 1
                        elif resource.get('format') == 'json':
                            analysis['json_resources'] += 1
                        
                        # Extraire les données si c'est une ressource intéressante
                        if (resource.get('format') in ['csv', 'json'] and 
                            resource.get('url') and 
                            resource.get('filesize', 0) > 1000):
                            
                            extracted_data = self.extract_data_from_resource(resource, dataset)
                            if extracted_data is not None:
                                analysis['extracted_data'].append(extracted_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path}: {e}")
            return None
    
    def extract_data_from_resource(self, resource, dataset):
        """Extrait les données d'une ressource avec découpage en chunks"""
        try:
            url = resource['url']
            format_type = resource['format']
            
            logger.info(f"Téléchargement de {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Erreur HTTP {response.status_code} pour {url}")
                return None
            
            # Découper en chunks pour éviter les problèmes de mémoire
            chunk_files = []
            
            if format_type == 'csv':
                # Lecture par chunks pour les CSV
                chunk_size = 200_000  # 200k lignes par chunk
                reader = pd.read_csv(io.StringIO(response.text), chunksize=chunk_size)
                
                for i, chunk in enumerate(reader):
                    # Nettoyage léger
                    chunk = chunk.dropna(subset=chunk.columns[:3])  # Garder les 3 premières colonnes non-nulles
                    
                    if not chunk.empty:
                        # Ajouter des métadonnées
                        chunk['source_file'] = dataset.get('title', 'Unknown')
                        chunk['source_organization'] = dataset.get('organization', {}).get('name', 'Unknown')
                        chunk['resource_url'] = url
                        chunk['extraction_date'] = datetime.now().isoformat()
                        chunk['file_format'] = format_type
                        
                        # Sauvegarder le chunk
                        chunk_file = self.analyzed_dir / f"chunk_{dataset.get('title', 'Unknown').replace(' ', '_')}_{i:04d}.parquet"
                        chunk.to_parquet(chunk_file, index=False)
                        chunk_files.append(chunk_file)
                        
                        logger.info(f"Chunk {i} sauvegardé: {chunk_file} ({len(chunk)} lignes)")
            
            elif format_type == 'json':
                json_data = response.json()
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    if 'data' in json_data:
                        df = pd.DataFrame(json_data['data'])
                    else:
                        df = pd.DataFrame([json_data])
                else:
                    return None
                
                if not df.empty:
                    # Ajouter des métadonnées
                    df['source_file'] = dataset.get('title', 'Unknown')
                    df['source_organization'] = dataset.get('organization', {}).get('name', 'Unknown')
                    df['resource_url'] = url
                    df['extraction_date'] = datetime.now().isoformat()
                    df['file_format'] = format_type
                    
                    # Sauvegarder le JSON (généralement plus petit)
                    json_file = self.analyzed_dir / f"json_{dataset.get('title', 'Unknown').replace(' ', '_')}.parquet"
                    df.to_parquet(json_file, index=False)
                    chunk_files.append(json_file)
                    
                    logger.info(f"JSON sauvegardé: {json_file} ({len(df)} lignes)")
            else:
                return None
            
            return {
                'chunk_files': chunk_files,
                'source': dataset.get('title', 'Unknown'),
                'url': url,
                'format': format_type
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de {resource.get('url', 'N/A')}: {e}")
            return None
    
    def analyze_all_files(self):
        """Analyse tous les fichiers JSON avec découpage en chunks"""
        logger.info("Début de l'analyse de tous les fichiers avec chunks")
        
        if not self.raw_dir.exists():
            logger.error(f"Dossier {self.raw_dir} non trouvé")
            return [], []
        
        files = [f for f in self.raw_dir.iterdir() if f.suffix == '.json']
        logger.info(f"Fichiers à analyser: {len(files)}")
        
        all_analyses = []
        all_chunk_files = []
        
        for i, file_path in enumerate(files):
            logger.info(f"Analyse {i+1}/{len(files)}: {file_path.name}")
            
            analysis = self.analyze_json_file(file_path)
            if analysis:
                all_analyses.append(analysis)
                
                # Collecter les chunks
                for extracted in analysis['extracted_data']:
                    if extracted and 'chunk_files' in extracted:
                        all_chunk_files.append(extracted['chunk_files'])
        
        return all_analyses, all_chunk_files
    
    def save_analyses(self, analyses):
        """Sauvegarde les analyses"""
        analysis_file = self.analyzed_dir / 'analyses.json'
        
        # Convertir les DataFrames en dict pour la sérialisation
        serializable_analyses = []
        for analysis in analyses:
            serializable_analysis = analysis.copy()
            serializable_analysis['extracted_data'] = [
                {
                    'source': data['source'],
                    'url': data['url'],
                    'format': data['format'],
                    'shape': data['dataframe'].shape
                }
                for data in analysis['extracted_data']
            ]
            serializable_analyses.append(serializable_analysis)
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_analyses, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analyses sauvegardées: {analysis_file}")
    
    def save_extracted_data(self, chunk_files_list):
        """Sauvegarde les données extraites en Parquet (déjà fait par chunks)"""
        logger.info(f"Traitement de {len(chunk_files_list)} groupes de chunks")
        
        # Compter le total de chunks
        total_chunks = 0
        for chunk_files in chunk_files_list:
            total_chunks += len(chunk_files)
        
        logger.info(f"Total de chunks créés: {total_chunks}")
        
        # Créer un index des chunks
        index_file = self.analyzed_dir / 'chunks_index.json'
        chunks_info = []
        
        for chunk_files in chunk_files_list:
            for chunk_file in chunk_files:
                try:
                    # Lire les métadonnées du chunk
                    df = pd.read_parquet(chunk_file)
                    chunks_info.append({
                        'file': str(chunk_file),
                        'shape': df.shape,
                        'source': df['source_file'].iloc[0] if 'source_file' in df.columns else 'Unknown',
                        'format': df['file_format'].iloc[0] if 'file_format' in df.columns else 'Unknown'
                    })
                except Exception as e:
                    logger.warning(f"Erreur lecture chunk {chunk_file}: {e}")
        
        # Sauvegarder l'index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Index des chunks sauvegardé: {index_file}")
        
        # Afficher un résumé
        self.print_chunks_summary(chunks_info)
    
    def print_chunks_summary(self, chunks_info):
        """Affiche un résumé des chunks"""
        logger.info("=" * 60)
        logger.info("RÉSUMÉ DES CHUNKS CRÉÉS")
        logger.info("=" * 60)
        logger.info(f"📊 Total chunks: {len(chunks_info)}")
        
        # Grouper par source
        sources = {}
        for chunk in chunks_info:
            source = chunk['source']
            if source not in sources:
                sources[source] = {'count': 0, 'total_rows': 0}
            sources[source]['count'] += 1
            sources[source]['total_rows'] += chunk['shape'][0]
        
        logger.info("📁 Par source:")
        for source, info in sources.items():
            logger.info(f"  - {source}: {info['count']} chunks, {info['total_rows']:,} lignes")
        
        logger.info("=" * 60)
    
    def print_summary(self, df):
        """Affiche un résumé des données"""
        logger.info("=" * 60)
        logger.info("RÉSUMÉ DES DONNÉES NETTOYÉES")
        logger.info("=" * 60)
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Colonnes: {list(df.columns)}")
        
        if 'source_file' in df.columns:
            logger.info("Sources:")
            for source in df['source_file'].unique():
                count = len(df[df['source_file'] == source])
                logger.info(f"  - {source}: {count} lignes")
        
        if 'file_format' in df.columns:
            logger.info("Formats:")
            for format_type in df['file_format'].unique():
                count = len(df[df['file_format'] == format_type])
                logger.info(f"  - {format_type}: {count} lignes")
    
    def run(self):
        """Lance l'analyse complète avec découpage en chunks"""
        logger.info("🚀 DÉBUT DE L'ANALYSE COMPLÈTE AVEC CHUNKS")
        logger.info("=" * 60)
        
        analyses, chunk_files_list = self.analyze_all_files()
        
        logger.info("✅ ANALYSE TERMINÉE")
        logger.info("=" * 60)
        logger.info(f"Fichiers analysés: {len(analyses)}")
        logger.info(f"Groupes de chunks: {len(chunk_files_list)}")
        
        # Sauvegarder les données par chunks
        if chunk_files_list:
            self.save_extracted_data(chunk_files_list)
        
        return analyses, chunk_files_list

if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.run()
