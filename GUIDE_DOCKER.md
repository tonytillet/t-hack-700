# 🐳 Guide Docker pour LUMEN

## 🎯 **Problème Résolu**

### **Avant Docker :**
- ❌ **Serveurs multiples** qui se lancent
- ❌ **Conflits de ports** (8080, 8081, 8082, etc.)
- ❌ **Processus Python** qui traînent
- ❌ **Difficultés de déploiement** sur différentes machines
- ❌ **Gestion manuelle** des dépendances

### **Avec Docker :**
- ✅ **Un seul conteneur** isolé
- ✅ **Port fixe** (8080) sans conflit
- ✅ **Environnement reproductible**
- ✅ **Déploiement simplifié**
- ✅ **Gestion automatique** des dépendances

## 🚀 **Démarrage Rapide**

### **1. Déploiement Automatique (Recommandé)**
```bash
# Sur la machine source
./deploy_docker.sh

# Sur la machine de destination
cd lumen_docker_*
./quick-start.sh
```

### **2. Démarrage Manuel**
```bash
# Construction de l'image
./docker-manage.sh build

# Démarrage du conteneur
./docker-manage.sh start
```

## 🐳 **Architecture Docker**

### **Fichiers Docker :**
- `Dockerfile` - Image de base Python 3.9
- `docker-compose.yml` - Configuration des services
- `docker-entrypoint.sh` - Script de démarrage
- `docker-manage.sh` - Gestion des conteneurs

### **Configuration :**
- **Port :** 8080 (fixe, pas de conflit)
- **Base :** Python 3.9-slim
- **Utilisateur :** Non-root (sécurité)
- **Volumes :** Données en lecture seule
- **Réseau :** Bridge isolé

## 🔧 **Commandes de Gestion**

### **Script `docker-manage.sh` :**

```bash
# Construction
./docker-manage.sh build

# Démarrage
./docker-manage.sh start

# Arrêt
./docker-manage.sh stop

# Redémarrage
./docker-manage.sh restart

# Logs en temps réel
./docker-manage.sh logs

# Statut du conteneur
./docker-manage.sh status

# Nettoyage complet
./docker-manage.sh clean

# Shell dans le conteneur
./docker-manage.sh shell

# Aide
./docker-manage.sh help
```

### **Commandes Docker Directes :**

```bash
# Construction
docker build -t lumen-app .

# Démarrage avec docker-compose
docker-compose up -d

# Arrêt
docker-compose down

# Logs
docker-compose logs -f

# Statut
docker-compose ps
```

## 📊 **Avantages Docker**

### **1. Isolation Complète**
- ✅ **Pas de conflits** avec d'autres applications
- ✅ **Port dédié** (8080) sans interférence
- ✅ **Environnement isolé** et sécurisé

### **2. Reproducibilité**
- ✅ **Même environnement** sur toutes les machines
- ✅ **Dépendances gérées** automatiquement
- ✅ **Configuration identique** partout

### **3. Gestion Simplifiée**
- ✅ **Un seul conteneur** à gérer
- ✅ **Démarrage/arrêt** en une commande
- ✅ **Logs centralisés**
- ✅ **Santé du conteneur** surveillée

### **4. Déploiement Facile**
- ✅ **Package unique** à déployer
- ✅ **Installation automatique** des dépendances
- ✅ **Configuration automatique**

## 🌐 **Accès aux Dashboards**

Une fois le conteneur démarré, LUMEN est accessible sur :

- **Menu Principal :** http://localhost:8080/
- **Bulletin Public :** http://localhost:8080/bulletin_lumen.html
- **Vue Pédagogique :** http://localhost:8080/dashboard_pedagogique.html
- **Carte des Risques :** http://localhost:8080/dashboard_risk_heatmap.html
- **Prédictions :** http://localhost:8080/dashboard_real_vs_predicted.html
- **Alertes Actives :** http://localhost:8080/dashboard_active_alerts.html

## 🔍 **Surveillance et Maintenance**

### **Vérification du Statut :**
```bash
./docker-manage.sh status
```

### **Logs en Temps Réel :**
```bash
./docker-manage.sh logs
```

### **Santé du Conteneur :**
- **Healthcheck** automatique toutes les 30s
- **Test** : curl http://localhost:8080/
- **Redémarrage** automatique en cas de problème

### **Nettoyage :**
```bash
./docker-manage.sh clean
```

## 🚨 **Résolution de Problèmes**

### **Port déjà utilisé :**
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8080

# Arrêter le conteneur
./docker-manage.sh stop
```

### **Conteneur ne démarre pas :**
```bash
# Voir les logs d'erreur
./docker-manage.sh logs

# Reconstruire l'image
./docker-manage.sh clean
./docker-manage.sh build
./docker-manage.sh start
```

### **Dashboards manquants :**
```bash
# Le conteneur les génère automatiquement au démarrage
# Vérifier les logs pour voir la génération
./docker-manage.sh logs
```

## 🎉 **Résultat Final**

### **Plus de Problèmes :**
- ❌ **Serveurs multiples** → ✅ **Un seul conteneur**
- ❌ **Conflits de ports** → ✅ **Port fixe isolé**
- ❌ **Processus traînants** → ✅ **Gestion automatique**
- ❌ **Déploiement complexe** → ✅ **Package Docker simple**

### **LUMEN Docker :**
- 🐳 **Isolé** et sécurisé
- 🚀 **Rapide** à déployer
- 🔧 **Facile** à gérer
- 📊 **Fiable** et reproductible

**LUMEN fonctionne maintenant parfaitement en Docker !** 🎯
