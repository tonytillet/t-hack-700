# 🚀 LUMEN - Méthodes de Démarrage

## 🐍 **MÉTHODE 1 : PYTHON DIRECT (Simple)**

### ✅ **Avantages :**
- Plus rapide
- Pas besoin de Docker
- Développement direct

### 📋 **Étapes :**
```bash
# 1. Générer les visualisations
python3 dashboard_integration.py

# 2. Lancer le serveur
python3 serveur_simple.py

# 3. Ouvrir http://localhost:8080/
```

---

## 🐳 **MÉTHODE 2 : DOCKER (Production)**

### ✅ **Avantages :**
- Environnement isolé
- Déploiement facile
- Configuration standardisée

### 📋 **Étapes :**
```bash
# 1. Construire l'image
docker build -t lumen-app .

# 2. Lancer le conteneur
docker run -d -p 8080:8080 --name lumen-container lumen-app

# 3. Ouvrir http://localhost:8080/
```

### 🔧 **Avec Docker Compose :**
```bash
# Lancer tout l'environnement
make dev
# ou
docker compose up --build
```

---

## 🎯 **RECOMMANDATION :**

### 🚀 **Pour le développement :**
```bash
python3 serveur_simple.py
```

### 🏭 **Pour la production :**
```bash
make dev
# ou
docker compose up --build
```

---

## 🛑 **ARRÊT :**

### Python direct :
```bash
pkill -f serveur_simple
```

### Docker :
```bash
docker stop lumen-container
docker rm lumen-container
```

### Docker Compose :
```bash
make stop
# ou
docker compose down
```

---

## 🔍 **VÉRIFICATION :**
```bash
# Vérifier que le serveur fonctionne
curl http://localhost:8080/

# Vérifier les processus
ps aux | grep python3
ps aux | grep docker
```

**Les deux méthodes fonctionnent !** 🎉
