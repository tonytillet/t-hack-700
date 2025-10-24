
#!/usr/bin/env python3
"""
Script de vérification des données disponibles
Usage: python3 verifier_donnees.py
"""

import json
import os
from datetime import datetime

def verifier_donnees():
    """Vérifie la disponibilité et la qualité des données collectées"""
    
    print('🔍 VÉRIFICATION DES DONNÉES DISPONIBLES')
    print('=======================================')
    print()
    
    # Statistiques globales
    total_fichiers = 0
    total_taille = 0
    donnees_simulees = 0
    donnees_reelles = 0
    
    # Vérifier data/search/data_gouv_fr/
    print('📊 DONNÉES DATA.GOUV.FR:')
    print('=======================')
    if os.path.exists('data/search/data_gouv_fr/'):
        fichiers = [f for f in os.listdir('data/search/data_gouv_fr/') if f.endswith('.json') and f != 'summary.json']
        print(f'✅ {len(fichiers)} fichiers trouvés')
        for fichier in fichiers[:5]:  # Afficher les 5 premiers
            taille = round(os.path.getsize(f'data/search/data_gouv_fr/{fichier}') / 1024, 2)
            print(f'  • {fichier} ({taille} KB)')
        if len(fichiers) > 5:
            print(f'  ... et {len(fichiers) - 5} autres fichiers')
        total_fichiers += len(fichiers)
    else:
        print('❌ Dossier data/search/data_gouv_fr/ non trouvé')
    
    print()
    
    # Vérifier data/search/insee/
    print('📊 DONNÉES INSEE:')
    print('=================')
    if os.path.exists('data/search/insee/'):
        fichiers = [f for f in os.listdir('data/search/insee/') if f.endswith('.json')]
        print(f'✅ {len(fichiers)} fichiers trouvés')
        for fichier in fichiers:
            taille = round(os.path.getsize(f'data/search/insee/{fichier}') / 1024, 2)
            print(f'  • {fichier} ({taille} KB)')
        total_fichiers += len(fichiers)
    else:
        print('❌ Dossier data/search/insee/ non trouvé')
    
    print()
    
    # Vérifier data/search/other/
    print('📊 DONNÉES AUTRES SOURCES:')
    print('==========================')
    if os.path.exists('data/search/other/'):
        fichiers = [f for f in os.listdir('data/search/other/') if f.endswith('.json')]
        print(f'✅ {len(fichiers)} fichiers trouvés')
        for fichier in fichiers:
            taille = round(os.path.getsize(f'data/search/other/{fichier}') / 1024, 2)
            print(f'  • {fichier} ({taille} KB)')
        total_fichiers += len(fichiers)
    else:
        print('❌ Dossier data/search/other/ non trouvé')
    
    print()
    
    # Vérifier la qualité des données
    print('🔍 VÉRIFICATION DE LA QUALITÉ:')
    print('==============================')
    
    # Vérifier les données simulées
    if os.path.exists('data/search/other/'):
        for fichier in os.listdir('data/search/other/'):
            if fichier.endswith('.json'):
                try:
                    with open(f'data/search/other/{fichier}', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'simulation' in str(data).lower() or 'simulé' in str(data).lower():
                        print(f'❌ {fichier}: DONNÉES SIMULÉES')
                        donnees_simulees += 1
                    else:
                        print(f'✅ {fichier}: DONNÉES RÉELLES')
                        donnees_reelles += 1
                except:
                    print(f'⚠️  {fichier}: Erreur de lecture')
    
    print()
    
    # Résumé final
    print('📈 RÉSUMÉ FINAL:')
    print('================')
    print(f'Total fichiers: {total_fichiers}')
    print(f'Données simulées: {donnees_simulees}')
    print(f'Données réelles: {donnees_reelles}')
    print(f'Taux de qualité: {round((donnees_reelles / (donnees_reelles + donnees_simulees)) * 100, 1)}%')
    
    if donnees_simulees > 0:
        print()
        print('⚠️  ATTENTION: Des données simulées ont été détectées!')
        print('Supprimez-les avant de construire le modèle.')
    else:
        print()
        print('✅ Toutes les données sont réelles!')
        print('Vous pouvez procéder à la construction du modèle.')

if __name__ == '__main__':
    verifier_donnees()
