# 🚀 LUMEN - Lancement Local

## 📋 **ÉTAPES SIMPLES :**

### 1️⃣ **Vérifier les fichiers essentiels**
```bash
ls -la dashboard_final_integration.html
ls -la serveur_simple.py
```

### 2️⃣ **Générer les visualisations (si nécessaire)**
```bash
python3 dashboard_integration.py
```

### 3️⃣ **Lancer le serveur**
```bash
python3 serveur_simple.py
```

### 4️⃣ **Ouvrir votre navigateur**
- **URL :** http://localhost:8080/
- **Dashboard automatique** s'ouvre

## 🌐 **URLS DISPONIBLES :**

- **🏠 Dashboard Principal :** http://localhost:8080/
- **🗺️ Carte Zones :** http://localhost:8080/dashboard_risk_heatmap.html
- **📈 Prédictions :** http://localhost:8080/dashboard_real_vs_predicted.html
- **🚨 Alertes :** http://localhost:8080/dashboard_active_alerts.html

## 🛑 **ARRÊTER LE SERVEUR :**
```bash
pkill -f serveur_simple
# ou Ctrl+C dans le terminal
```

## 🔧 **EN CAS DE PROBLÈME :**

### Port déjà utilisé :
```bash
pkill -f python3
python3 serveur_simple.py
```

### Fichiers manquants :
```bash
python3 dashboard_integration.py
python3 serveur_simple.py
```

### Vérifier le statut :
```bash
curl http://localhost:8080/
```

## ✅ **RÉSULTAT ATTENDU :**
- Serveur démarré sur port 8080
- Dashboard LUMEN accessible
- Toutes les visualisations fonctionnelles
- Un seul port pour tout !

**C'est tout ! Simple et efficace.** 🎉
