# 🔧 Guide de Dépannage - Dashboards Manquants

## 🚨 **Problème : "Pleins de dashboards manquants et le serveur ne veut pas démarrer"**

### **🔍 Diagnostic Automatique**

```bash
# 1. Vérifier l'état des dashboards
./check_files.sh

# 2. Réparer automatiquement les dashboards manquants
./fix_missing_dashboards.sh

# 3. Lancer le projet
./start.sh
```

### **🛠️ Solutions par Étape**

#### **Étape 1 : Vérification Complète**
```bash
# Vérifier tous les dashboards requis
./check_files.sh
```

**Dashboards Requis (8 au total) :**
- ✅ `index.html` - Page d'accueil
- ✅ `dashboard_final_integration.html` - Dashboard principal
- ✅ `bulletin_lumen.html` - Bulletin public
- ✅ `dashboard_pedagogique.html` - Vue pédagogique
- ✅ `dashboard_simplifie.html` - Vue simplifiée
- ✅ `dashboard_risk_heatmap.html` - Carte des zones à risque
- ✅ `dashboard_real_vs_predicted.html` - Graphiques réel vs prédit
- ✅ `dashboard_active_alerts.html` - Panneau des alertes actives

#### **Étape 2 : Réparation Automatique**
```bash
# Script de réparation intelligent
./fix_missing_dashboards.sh
```

**Ce script :**
- 🔍 **Détecte** les dashboards manquants
- 🎨 **Génère** les dashboards dynamiques via `dashboard_integration.py`
- 🛠️ **Crée** des templates de base pour les dashboards manquants
- ✅ **Vérifie** que tous les dashboards sont présents

#### **Étape 3 : Génération Complète (si nécessaire)**
```bash
# Génération complète de tous les dashboards
python3 generate_all_dashboards.py
```

#### **Étape 4 : Lancement du Projet**
```bash
# Le script start.sh répare automatiquement les dashboards
./start.sh
```

### **🔧 Solutions Manuelles**

#### **Si `fix_missing_dashboards.sh` ne fonctionne pas :**

1. **Vérifier Python :**
```bash
python3 --version
# Doit être Python 3.7+
```

2. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

3. **Générer manuellement :**
```bash
# Génération des dashboards dynamiques
python3 dashboard_integration.py

# Ou génération complète
python3 generate_all_dashboards.py
```

4. **Créer les templates manquants :**
```bash
# Le script fix_missing_dashboards.sh crée automatiquement
# des templates HTML de base pour les dashboards manquants
```

### **📋 Vérification Post-Réparation**

```bash
# Vérifier que tous les dashboards sont présents
ls -la dashboard_*.html index.html bulletin_lumen.html

# Vérifier les permissions
chmod +x *.sh

# Tester le serveur
./start.sh
```

### **🚀 Déploiement sur Nouvelle Machine**

#### **Méthode 1 : Script de Déploiement (Recommandé)**
```bash
# Sur la machine source
./deploy.sh

# Sur la machine de destination
scp -r lumen_deploy_* user@machine:/path/
ssh user@machine
cd /path/lumen_deploy_*
./start.sh  # Répare automatiquement les dashboards
```

#### **Méthode 2 : Copie Manuelle + Réparation**
```bash
# Copier tous les fichiers
scp -r * user@machine:/path/

# Sur la machine de destination
cd /path/
chmod +x *.sh
./fix_missing_dashboards.sh
./start.sh
```

### **⚠️ Problèmes Courants**

#### **1. "Permission denied"**
```bash
chmod +x *.sh
```

#### **2. "Python not found"**
```bash
# Installer Python 3.7+
# Ubuntu/Debian: sudo apt install python3 python3-pip
# macOS: brew install python3
# Windows: https://python.org/downloads/
```

#### **3. "Module not found"**
```bash
pip install -r requirements.txt
```

#### **4. "Port already in use"**
```bash
pkill -f python3
./start.sh
```

### **🎯 Solution Définitive**

**Le script `start.sh` a été amélioré pour :**
- ✅ **Vérifier automatiquement** tous les dashboards
- ✅ **Réparer automatiquement** les dashboards manquants
- ✅ **Générer des templates** pour les dashboards manquants
- ✅ **Garantir le démarrage** du serveur

**Plus jamais de problème de dashboards manquants !** 🎉

### **📞 Support**

Si le problème persiste :
1. Vérifiez que tous les fichiers sont copiés
2. Vérifiez les permissions (`chmod +x *.sh`)
3. Vérifiez Python et les dépendances
4. Utilisez `./fix_missing_dashboards.sh` manuellement
