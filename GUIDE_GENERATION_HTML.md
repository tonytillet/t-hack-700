# 🎨 Guide de Génération des Dashboards HTML

## 📋 **Scripts de Génération HTML**

### **1. Script Principal : `dashboard_integration.py`**

**Ce que fait ce script :**
- 📊 **Charge les données** et le modèle ML le plus récent
- 🔮 **Génère les prédictions** pour toutes les données
- 🗺️ **Crée la carte des zones à risque** (`dashboard_risk_heatmap.html`)
- 📈 **Génère le graphique réel vs prédit** (`dashboard_real_vs_predicted.html`)
- 🚨 **Crée le panneau des alertes actives** (`dashboard_active_alerts.html`)
- 📋 **Génère un rapport d'intégrité** JSON

**Comment l'utiliser :**
```bash
python3 dashboard_integration.py
```

### **2. Script Automatisé : `generate_dashboards.sh`**

**Ce que fait ce script :**
- ✅ **Vérifie les prérequis** (Python, fichiers)
- 🎨 **Lance la génération** des dashboards
- 📁 **Affiche les fichiers créés**

**Comment l'utiliser :**
```bash
./generate_dashboards.sh
```

### **3. Intégration Automatique dans `start.sh`**

**Le script `start.sh` génère automatiquement les dashboards si :**
- Les fichiers HTML n'existent pas
- Le script `generate_dashboards.sh` est disponible
- Ou directement via `dashboard_integration.py`

## 🎯 **Fichiers HTML Générés**

### **1. `dashboard_risk_heatmap.html`**
- **Contenu :** Carte interactive des zones à risque
- **Technologie :** Plotly + Mapbox
- **Données :** Scores de risque par région
- **Taille :** ~4.8 MB (graphiques interactifs)

### **2. `dashboard_real_vs_predicted.html`**
- **Contenu :** Graphique de comparaison réel vs prédit
- **Technologie :** Plotly
- **Données :** Évolution temporelle des prédictions
- **Taille :** ~4.8 MB (graphiques interactifs)

### **3. `dashboard_active_alerts.html`**
- **Contenu :** Panneau des alertes actives
- **Technologie :** HTML/CSS pur
- **Données :** Alertes par région et niveau
- **Taille :** ~3 KB (texte simple)

## 🔧 **Processus de Génération**

### **Étape 1 : Chargement des Données**
```python
# Charge les données depuis data/processed/dataset.parquet
# Ou génère des données de démonstration si absent
```

### **Étape 2 : Chargement du Modèle**
```python
# Charge le modèle ML le plus récent depuis models/
# Ou entraîne un nouveau modèle si absent
```

### **Étape 3 : Génération des Prédictions**
```python
# Prédit le taux de grippe pour toutes les données
# Calcule les scores de risque (0-100)
# Détermine les niveaux d'alerte (VERT, JAUNE, ORANGE, ROUGE)
```

### **Étape 4 : Création des Visualisations**
```python
# Carte des zones à risque avec Plotly + Mapbox
# Graphiques temporels avec Plotly
# Panneau d'alertes en HTML/CSS
```

## 📊 **Données Utilisées**

### **Features du Modèle :**
- `population` - Population de la région
- `temperature_moyenne` - Température moyenne
- `humidite_moyenne` - Humidité moyenne
- `passages_urgences_grippe` - Passages aux urgences
- `taux_incidence` - Taux d'incidence
- `couverture_vaccinale` - Couverture vaccinale
- `google_trends_grippe` - Tendances Google
- `indice_lumen` - Indice LUMEN
- **+ Features temporelles** (jour_semaine, mois, saison)
- **+ Features dérivées** (moyennes mobiles, lags)

### **Régions Couvertes :**
- Grand Est
- Île-de-France
- Auvergne-Rhône-Alpes
- Provence-Alpes-Côte d'Azur
- Occitanie
- Nouvelle-Aquitaine
- Hauts-de-France

## 🚀 **Utilisation Recommandée**

### **Pour le Développement :**
```bash
# Générer manuellement les dashboards
python3 dashboard_integration.py
```

### **Pour le Déploiement :**
```bash
# Le script start.sh génère automatiquement les dashboards
./start.sh
```

### **Pour la Production :**
```bash
# Génération programmée (cron)
0 */6 * * * cd /path/to/lumen && python3 dashboard_integration.py
```

## ⚠️ **Points d'Attention**

1. **Taille des Fichiers :** Les fichiers Plotly sont volumineux (~5MB)
2. **Dépendances :** Nécessite pandas, numpy, plotly, scikit-learn
3. **Données :** Génère des données de démonstration si les vraies données sont absentes
4. **Performance :** La génération peut prendre quelques secondes

## 🎉 **Résultat**

**Tous les dashboards sont maintenant générés automatiquement !** 🎨

Le système LUMEN est **100% autonome** et génère ses propres visualisations à partir des données et du modèle ML.
