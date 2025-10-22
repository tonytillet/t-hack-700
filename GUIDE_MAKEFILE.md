# 🚀 Guide Makefile - LUMEN

## 🎯 **Commande Principale**

### **Démarrage Rapide :**
```bash
make dev
```

**Cette commande :**
- ✅ **Détecte automatiquement** Docker ou Local
- ✅ **Lance LUMEN** dans le mode approprié
- ✅ **Génère automatiquement** les dashboards manquants
- ✅ **Affiche l'URL** d'accès

## 📋 **Toutes les Commandes Disponibles**

### **🚀 Démarrage :**
```bash
make dev      # Démarrage rapide (Docker ou Local)
make docker   # Démarrage en mode Docker
make local    # Démarrage en mode Local
```

### **🐳 Gestion Docker :**
```bash
make build    # Construire l'image Docker
make start    # Démarrer le conteneur Docker
make stop     # Arrêter le conteneur Docker
make restart   # Redémarrer le conteneur Docker
make logs     # Afficher les logs du conteneur
make status   # Afficher le statut du conteneur
```

### **🔧 Maintenance :**
```bash
make check    # Vérifier les fichiers essentiels
make fix      # Réparer les dashboards manquants
make deps     # Installer les dépendances Python
make test     # Tester l'accès web
make clean    # Nettoyer les conteneurs et images
make cleanup  # Nettoyage agressif du projet
```

### **📦 Déploiement :**
```bash
make deploy-docker  # Créer le package Docker
make deploy        # Créer le package universel
```

### **ℹ️ Informations :**
```bash
make help     # Afficher l'aide
make info     # Afficher les informations du projet
```

## 🎯 **Utilisation Recommandée**

### **Pour le Développement :**
```bash
# Démarrage rapide
make dev

# Vérifier le statut
make status

# Voir les logs
make logs

# Arrêter
make stop
```

### **Pour la Production :**
```bash
# Créer le package de déploiement
make deploy

# Sur la machine de destination
cd lumen_universal_*
make dev
```

### **Pour le Débogage :**
```bash
# Vérifier les fichiers
make check

# Réparer les dashboards
make fix

# Tester l'accès
make test

# Voir les logs
make logs
```

## 🌐 **Accès aux Dashboards**

Une fois `make dev` exécuté, LUMEN est accessible sur :

- **Menu Principal :** http://localhost:8080/
- **Bulletin Public :** http://localhost:8080/bulletin_lumen.html
- **Vue Pédagogique :** http://localhost:8080/dashboard_pedagogique.html
- **Carte des Risques :** http://localhost:8080/dashboard_risk_heatmap.html
- **Prédictions :** http://localhost:8080/dashboard_real_vs_predicted.html
- **Alertes Actives :** http://localhost:8080/dashboard_active_alerts.html

## 🔧 **Résolution de Problèmes**

### **Si `make dev` ne fonctionne pas :**
```bash
# Vérifier les fichiers
make check

# Réparer les dashboards
make fix

# Réessayer
make dev
```

### **Si Docker ne fonctionne pas :**
```bash
# Forcer le mode local
make local
```

### **Si le conteneur ne démarre pas :**
```bash
# Voir les logs
make logs

# Nettoyer et reconstruire
make clean
make build
make start
```

## 🎉 **Avantages du Makefile**

### **Simplicité :**
- ✅ **Une seule commande** : `make dev`
- ✅ **Détection automatique** Docker/Local
- ✅ **Gestion complète** du cycle de vie

### **Flexibilité :**
- ✅ **Mode Docker** pour la production
- ✅ **Mode Local** pour le développement
- ✅ **Commandes spécialisées** pour chaque besoin

### **Maintenance :**
- ✅ **Vérification automatique** des fichiers
- ✅ **Réparation automatique** des dashboards
- ✅ **Nettoyage facile** des ressources

## 🚀 **Exemple d'Utilisation Complète**

```bash
# 1. Démarrage
make dev

# 2. Vérification
make status
make test

# 3. Développement
make logs    # Voir les logs en temps réel

# 4. Arrêt
make stop

# 5. Nettoyage
make clean
```

## 🎯 **Résultat Final**

**Avec le Makefile, LUMEN se lance en une seule commande :**

```bash
make dev
```

**C'est tout ! Plus besoin de se souvenir de commandes complexes !** 🎉
