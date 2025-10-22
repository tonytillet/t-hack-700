# 🚀 Guide de Déploiement LUMEN

## 📋 Problème Résolu

Le script `start.sh` modifiait le fichier `serveur_simple.py` en place, ce qui causait des problèmes sur d'autres machines. **Maintenant, le script utilise une copie temporaire** qui ne modifie jamais les fichiers originaux.

## 🔧 Solution Implémentée

### 1. **Script `start.sh` Amélioré**
- ✅ **Ne modifie plus** `serveur_simple.py` original
- ✅ **Crée une copie temporaire** `serveur_temp.py`
- ✅ **Détection automatique** du port libre
- ✅ **Nettoyage automatique** des fichiers temporaires

### 2. **Script de Vérification `check_files.sh`**
- ✅ **Vérifie tous les fichiers essentiels**
- ✅ **Corrige automatiquement** les permissions
- ✅ **Rapport détaillé** de l'état du projet

### 3. **Script de Déploiement `deploy.sh`**
- ✅ **Crée un package complet** pour déploiement
- ✅ **Inclut tous les fichiers nécessaires**
- ✅ **Instructions claires** pour la machine cible

## 🚀 Instructions de Déploiement

### **Sur la machine source :**

```bash
# 1. Vérifier que tout fonctionne
./check_files.sh

# 2. Créer un package de déploiement
./deploy.sh

# 3. Le script crée un dossier "lumen_deploy_YYYYMMDD_HHMMSS"
```

### **Sur la machine de destination :**

```bash
# 1. Copier le dossier de déploiement
scp -r lumen_deploy_* user@machine:/path/to/destination/

# 2. Se connecter à la machine
ssh user@machine

# 3. Aller dans le dossier
cd /path/to/destination/lumen_deploy_*

# 4. Vérifier les fichiers
./check_files.sh

# 5. Lancer le projet
./start.sh
```

## 📁 Fichiers Inclus dans le Déploiement

### **Fichiers Essentiels :**
- `serveur_simple.py` - Serveur web principal
- `index.html` - Page d'accueil
- `dashboard_final_integration.html` - Dashboard principal
- `bulletin_lumen.html` - Bulletin public
- `dashboard_pedagogique.html` - Vue pédagogique
- `dashboard_risk_heatmap.html` - Carte des risques
- `dashboard_real_vs_predicted.html` - Prédictions
- `dashboard_active_alerts.html` - Alertes actives
- `requirements.txt` - Dépendances Python

### **Scripts Utilitaires :**
- `start.sh` - Lancement automatique
- `clean.sh` - Nettoyage des processus
- `check_files.sh` - Vérification des fichiers
- `deploy.sh` - Création du package

### **Dossiers de Données :**
- `ml/` - Modèles et artefacts ML
- `data/` - Données (si présentes)
- `explicabilite/` - Rapports d'explicabilité
- `monitoring/` - Configuration de monitoring
- `models/` - Modèles sauvegardés

## ✅ Avantages de la Nouvelle Solution

1. **🔒 Fichiers originaux préservés** - Jamais modifiés
2. **🌐 Port automatique** - Détection intelligente des ports libres
3. **🧹 Nettoyage automatique** - Suppression des fichiers temporaires
4. **📋 Vérification complète** - Contrôle de l'intégrité
5. **🚀 Déploiement simple** - Un seul script pour tout

## 🎯 Résultat

**Maintenant, le projet fonctionne identiquement sur toutes les machines !** 🎉

Le script `start.sh` est **100% portable** et ne modifie jamais les fichiers originaux.
