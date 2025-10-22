# 🚀 LUMEN Enhanced - Guide de Lancement

## 📋 **Prérequis**
- Python 3.7+ installé
- Git installé

## 🔧 **Installation et Lancement**

### 1. **Cloner le projet**
```bash
git clone <votre-repo-url>
cd t-hack-700
```

### 2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

### 3. **Lancer le serveur**
```bash
python3 serveur_simple.py
```

### 4. **Accéder au projet**
Ouvrez votre navigateur sur : **http://localhost:8082/**

---

## 🎯 **Dashboards Disponibles**

### 📊 **Menu Principal**
- **URL** : http://localhost:8082/
- **Description** : Interface unifiée avec navigation vers tous les dashboards

### 🔔 **Bulletin Public**
- **URL** : http://localhost:8082/bulletin_lumen.html
- **Description** : Résumé automatique pour le grand public

### 📚 **Dashboard Pédagogique**
- **URL** : http://localhost:8082/dashboard_pedagogique.html
- **Description** : Indicateurs simplifiés avec jauges colorées

### 🗺️ **Carte des Risques**
- **URL** : http://localhost:8082/dashboard_risk_heatmap.html
- **Description** : Visualisation géographique des zones à risque

### 📈 **Prédictions**
- **URL** : http://localhost:8082/dashboard_real_vs_predicted.html
- **Description** : Comparaison prédictions vs réalité

### 🚨 **Alertes Actives**
- **URL** : http://localhost:8082/dashboard_active_alerts.html
- **Description** : Surveillance en temps réel

---

## 🛠️ **Commandes Utiles**

### **Démarrer le projet**
```bash
python3 serveur_simple.py
```

### **Arrêter le serveur**
```bash
# Dans le terminal où le serveur tourne
Ctrl + C

# Ou depuis un autre terminal
pkill -f python3
```

### **Vérifier que le serveur fonctionne**
```bash
curl http://localhost:8082/
```

### **Changer le port (si 8082 est occupé)**
Éditez le fichier `serveur_simple.py` et changez :
```python
PORT = 8082  # Changez ce numéro
```

---

## 🔄 **Mise à Jour des Données**

### **Générer les visualisations**
```bash
python3 dashboard_integration.py
```

### **Générer l'explicabilité SHAP**
```bash
python3 explicabilite_shap.py
```

### **Entraîner le modèle ML**
```bash
python3 ml/train_random_forest.py
```

---

## 🐳 **Alternative Docker (Optionnel)**

### **Avec Docker Compose**
```bash
docker compose up --build
```

### **Avec Make**
```bash
make dev
```

---

## ❗ **Dépannage**

### **Port déjà utilisé**
```bash
# Trouver le processus qui utilise le port
lsof -i :8082

# Tuer le processus
kill -9 <PID>
```

### **Erreur de dépendances**
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### **Fichiers manquants**
```bash
# Générer les dashboards
python3 dashboard_integration.py
```

---

## 📱 **Accès Mobile**

Le projet est responsive et fonctionne sur mobile :
- Ouvrez http://localhost:8082/ sur votre téléphone
- Assurez-vous d'être sur le même réseau WiFi

---

## 🎉 **C'est parti !**

Une fois le serveur lancé, vous devriez voir :
```
🌐 LUMEN - SERVEUR UNIFIÉ
========================================
🚀 Port unique: 8082
📊 Dashboard: http://localhost:8082/
🗺️ Carte: http://localhost:8082/dashboard_risk_heatmap.html
📈 Prédictions: http://localhost:8082/dashboard_real_vs_predicted.html
🚨 Alertes: http://localhost:8082/dashboard_active_alerts.html
🔔 Bulletin: http://localhost:8082/bulletin_lumen.html
📚 Pédagogique: http://localhost:8082/dashboard_pedagogique.html
========================================
✅ Dashboard prêt
🌐 Serveur: http://localhost:8082
🛑 Ctrl+C pour arrêter
```

**Ouvrez http://localhost:8082/ dans votre navigateur !** 🚀
