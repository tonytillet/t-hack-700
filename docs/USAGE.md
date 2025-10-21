# 🚀 Utilisation

## Interface principale

L'application LUMEN propose 5 onglets principaux :

### 1. 🗺️ Carte des alertes
Visualisation géographique interactive des régions à risque.

**Fonctionnalités :**
- Carte de France avec code couleur par niveau d'alerte
- Clic sur une région pour voir les détails
- Légende dynamique des niveaux de risque
- Zoom et navigation

**Niveaux d'alerte :**
- 🟢 **Vert** : Risque faible (score < 40)
- 🟡 **Jaune** : Risque modéré (40-60)
- 🟠 **Orange** : Risque élevé (60-80)
- 🔴 **Rouge** : Risque critique (> 80)

### 2. 📊 Tableau de bord
Vue d'ensemble des alertes actives en temps réel.

**Indicateurs clés :**
- Nombre de régions en alerte
- Score moyen national
- Tendance hebdomadaire
- Statistiques par région

**Graphiques disponibles :**
- Évolution temporelle des alertes
- Comparaison inter-régions
- Distribution des scores

### 3. 📋 Protocoles d'action
Actions recommandées avec coûts et ROI estimés.

**Types de protocoles :**
- Campagnes de vaccination ciblées
- Communication santé publique
- Renforcement de la surveillance
- Mobilisation des ressources

**Informations par protocole :**
- Coût estimé
- ROI (retour sur investissement)
- Timeline de mise en œuvre
- Ressources nécessaires

### 4. 🔍 Analyse détaillée
Exploration approfondie d'une région spécifique.

**Données disponibles :**
- Historique des alertes
- Prédictions sur 4 semaines
- Analyse des facteurs de risque
- Comparaison avec années précédentes

### 5. ⚙️ Configuration
Ajustement des paramètres du système.

**Réglages disponibles :**
- Seuils d'alerte personnalisables
- Choix des sources de données
- Fréquence de mise à jour
- Niveau de sensibilité

## Export des données

### CSV des alertes
Exportez la liste complète des alertes avec priorités.

```bash
# Fichier généré
data/alerts/alertes_YYYYMMDD_HHMMSS.csv
```

**Colonnes :**
- region
- level (CRITIQUE, ÉLEVÉ, MODÉRÉ)
- alert_score
- action
- timeline

### Rapports régionaux
Analysez chaque région individuellement.

**Contenu du rapport :**
- Statistiques détaillées
- Graphiques d'évolution
- Recommandations d'action
- Prédictions à 4 semaines

### Métriques de performance
Suivez l'efficacité du système d'alerte.

**Indicateurs :**
- Taux de détection
- Faux positifs/négatifs
- Temps d'avance des alertes
- Précision des prédictions

## Automatisation

### Lancement automatique

Créer un script pour lancer l'application au démarrage :

**Linux/Mac :**
```bash
#!/bin/bash
cd /path/to/t-hack-700
source venv/bin/activate
python launch_app.py
```

**Windows :**
```cmd
@echo off
cd C:\path\to\t-hack-700
call venv\Scripts\activate
python launch_app.py
```

### Mise à jour automatique des données

Programmer la collecte de données avec cron (Linux/Mac) :

```bash
# Tous les lundis à 8h
0 8 * * 1 cd /path/to/t-hack-700 && venv/bin/python scripts/generate_demo_data.py
```

Ou avec le Planificateur de tâches Windows.

## Accès distant

Pour accéder à l'application depuis un autre ordinateur du réseau :

```bash
# Trouver l'IP locale
ifconfig  # Linux/Mac
ipconfig  # Windows

# L'application est accessible sur
http://<IP_LOCALE>:8501
```

**Note :** Par défaut, Streamlit est accessible depuis le réseau local.
