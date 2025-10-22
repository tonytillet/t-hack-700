# 🚀 LUMEN - Processus de Démarrage Complet

## 📋 Table des Matières
- [Vue d'ensemble](#vue-densemble)
- [Méthode 1 : Script Automatique](#méthode-1--script-automatique-recommandé)
- [Méthode 2 : Lancement Manuel](#méthode-2--lancement-manuel)
- [Méthode 3 : Docker](#méthode-3--docker)
- [Vérifications et Diagnostics](#vérifications-et-diagnostics)
- [Résolution des Problèmes](#résolution-des-problèmes)

---

## 🎯 Vue d'ensemble

LUMEN peut être lancé de **3 manières différentes** :
1. **Script automatique** (`start.sh`) - **Recommandé** ✅
2. **Lancement manuel** (commandes Python)
3. **Docker** (conteneurisation)

Chaque méthode a ses avantages selon le contexte d'utilisation.

---

## 🚀 Méthode 1 : Script Automatique (Recommandé)

### Avantages
- ✅ **Automatique** : Tout est géré par le script
- ✅ **Intelligent** : Détecte et résout les problèmes
- ✅ **Rapide** : Une seule commande
- ✅ **Sûr** : Vérifications avant lancement

### Commande
```bash
./start.sh
```

### Processus Détaillé

#### Étape 1 : Vérifications Préliminaires (5 secondes)

**1.1 Vérification de Python**
```bash
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi
```
- Vérifie que Python 3 est installé
- Affiche un message d'erreur si absent
- **Sortie attendue** : Aucune (si Python est installé)

**1.2 Vérification du fichier requirements.txt**
```bash
if [ ! -f "requirements.txt" ]; then
    echo "❌ Fichier requirements.txt manquant"
    exit 1
fi
```
- Vérifie la présence du fichier de dépendances
- **Sortie attendue** : Aucune (si le fichier existe)

**1.3 Installation des dépendances**
```bash
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1
```
- Installe toutes les dépendances Python
- Sortie redirigée vers `/dev/null` (silencieux)
- **Durée** : 5-30 secondes (selon si déjà installées)
- **Sortie attendue** :
  ```
  📦 Vérification des dépendances...
  ```

**1.4 Vérification des fichiers essentiels**
```bash
if [ ! -f "serveur_simple.py" ]; then
    echo "❌ Fichier serveur_simple.py manquant"
    exit 1
fi
```
- Vérifie que le serveur existe
- **Sortie attendue** : Aucune (si le fichier existe)

---

#### Étape 2 : Nettoyage de l'Environnement (2 secondes)

**2.1 Arrêt des processus Python existants**
```bash
echo "🛑 Arrêt des processus existants..."
pkill -f python3 2>/dev/null || true
```
- Tue tous les processus Python en cours
- Évite les conflits de port
- **Sortie attendue** :
  ```
  🛑 Arrêt des processus existants...
  ```

**2.2 Attente de libération des ressources**
```bash
sleep 2
```
- Attend 2 secondes pour que les ports se libèrent
- Garantit un démarrage propre

---

#### Étape 3 : Détection d'un Port Libre (< 1 seconde)

**3.1 Recherche d'un port disponible**
```bash
PORT=8081
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done
```
- Commence par le port 8081
- Incrémente jusqu'à trouver un port libre
- Utilise `lsof` pour vérifier l'occupation
- **Sortie attendue** : Aucune (interne)

**3.2 Affichage du port trouvé**
```bash
echo "🚀 Lancement sur le port $PORT..."
```
- **Sortie attendue** :
  ```
  🚀 Lancement sur le port 8081...
  ```

---

#### Étape 4 : Configuration Dynamique (< 1 seconde)

**4.1 Modification du port dans le serveur**
```bash
sed -i.tmp "s/PORT = [0-9]*/PORT = $PORT/" serveur_simple.py
```
- Utilise `sed` pour modifier le fichier
- Crée une sauvegarde `.tmp` avant modification
- Remplace `PORT = 8080` par `PORT = 8081` (ou autre)
- **Fichier modifié** : `serveur_simple.py`
- **Sauvegarde créée** : `serveur_simple.py.tmp`

---

#### Étape 5 : Lancement du Serveur (3 secondes)

**5.1 Démarrage du serveur en arrière-plan**
```bash
python3 serveur_simple.py &
```
- Lance le serveur en mode background (`&`)
- Libère le terminal pour la suite
- **Processus créé** : `python3 serveur_simple.py`

**5.2 Attente du démarrage**
```bash
sleep 3
```
- Attend 3 secondes pour que le serveur démarre complètement
- Garantit que le serveur est prêt avant vérification

---

#### Étape 6 : Vérification du Démarrage (< 1 seconde)

**6.1 Test de connexion**
```bash
if curl -s http://localhost:$PORT/ > /dev/null; then
    echo "✅ Serveur LUMEN lancé avec succès !"
else
    echo "❌ Erreur lors du lancement du serveur"
    exit 1
fi
```
- Utilise `curl` pour tester la connexion
- Vérifie que le serveur répond
- **Sortie attendue** (si succès) :
  ```
  ✅ Serveur LUMEN lancé avec succès !
  🌐 Accédez au projet : http://localhost:8081/
  ```

**6.2 Affichage des URLs disponibles**
```bash
echo "📊 Dashboards disponibles :"
echo "   • Menu Principal    : http://localhost:$PORT/"
echo "   • Bulletin Public   : http://localhost:$PORT/bulletin_lumen.html"
echo "   • Vue Pédagogique   : http://localhost:$PORT/dashboard_pedagogique.html"
echo "   • Carte des Risques : http://localhost:$PORT/dashboard_risk_heatmap.html"
echo "   • Prédictions       : http://localhost:$PORT/dashboard_real_vs_predicted.html"
echo "   • Alertes Actives   : http://localhost:$PORT/dashboard_active_alerts.html"
```
- Liste toutes les URLs accessibles
- **Sortie attendue** :
  ```
  📊 Dashboards disponibles :
     • Menu Principal    : http://localhost:8081/
     • Bulletin Public   : http://localhost:8081/bulletin_lumen.html
     • Vue Pédagogique   : http://localhost:8081/dashboard_pedagogique.html
     • Carte des Risques : http://localhost:8081/dashboard_risk_heatmap.html
     • Prédictions       : http://localhost:8081/dashboard_real_vs_predicted.html
     • Alertes Actives   : http://localhost:8081/dashboard_active_alerts.html
  ```

---

#### Étape 7 : Ouverture du Navigateur (< 1 seconde)

**7.1 Détection du système d'exploitation**
```bash
if command -v open &> /dev/null; then
    echo "🌐 Ouverture automatique du navigateur..."
    open http://localhost:$PORT/
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Ouverture automatique du navigateur..."
    xdg-open http://localhost:$PORT/
fi
```
- Utilise `open` sur **macOS**
- Utilise `xdg-open` sur **Linux**
- Ouvre automatiquement le navigateur par défaut
- **Sortie attendue** :
  ```
  🌐 Ouverture automatique du navigateur...
  ```

---

#### Étape 8 : Maintien du Serveur

**8.1 Attente de l'arrêt**
```bash
wait
```
- Maintient le script actif
- Attend que l'utilisateur arrête le serveur (Ctrl+C)
- **Sortie attendue** :
  ```
  🛑 Pour arrêter : Ctrl+C ou 'pkill -f python3'
  ```

**8.2 Nettoyage à l'arrêt**
```bash
rm -f serveur_simple.py.tmp
```
- Supprime le fichier temporaire créé par `sed`
- Exécuté automatiquement à la fin

---

### Sortie Complète Attendue

```
🧠 LUMEN Enhanced - Démarrage du Système
========================================
📦 Vérification des dépendances...
🛑 Arrêt des processus existants...
🚀 Lancement sur le port 8081...

✅ Serveur LUMEN lancé avec succès !
🌐 Accédez au projet : http://localhost:8081/

📊 Dashboards disponibles :
   • Menu Principal    : http://localhost:8081/
   • Bulletin Public   : http://localhost:8081/bulletin_lumen.html
   • Vue Pédagogique   : http://localhost:8081/dashboard_pedagogique.html
   • Carte des Risques : http://localhost:8081/dashboard_risk_heatmap.html
   • Prédictions       : http://localhost:8081/dashboard_real_vs_predicted.html
   • Alertes Actives   : http://localhost:8081/dashboard_active_alerts.html

🛑 Pour arrêter : Ctrl+C ou 'pkill -f python3'

🌐 Ouverture automatique du navigateur...
```

---

### Durée Totale
- **Première fois** : ~30-60 secondes (installation des dépendances)
- **Lancements suivants** : ~10 secondes

---

## 🔧 Méthode 2 : Lancement Manuel

### Avantages
- ✅ **Contrôle total** : Vous gérez chaque étape
- ✅ **Débogage facile** : Voir les erreurs en direct
- ✅ **Flexible** : Personnaliser le processus

### Processus Complet

#### Étape 1 : Préparation de l'Environnement

**1.1 Créer un environnement virtuel (recommandé)**
```bash
python3 -m venv venv
```
- Crée un environnement Python isolé
- **Durée** : 5-10 secondes
- **Répertoire créé** : `venv/`

**1.2 Activer l'environnement virtuel**
```bash
# Sur macOS/Linux
source venv/bin/activate

# Sur Windows
venv\Scripts\activate
```
- Active l'environnement virtuel
- **Indicateur** : `(venv)` apparaît dans le terminal

**1.3 Installer les dépendances**
```bash
pip install -r requirements.txt
```
- Installe toutes les dépendances
- **Durée** : 30-120 secondes (première fois)
- **Sortie attendue** :
  ```
  Collecting pandas
  Collecting numpy
  ...
  Successfully installed pandas-2.0.0 numpy-1.24.0 ...
  ```

---

#### Étape 2 : Génération des Dashboards

**2.1 Exécuter le script de génération**
```bash
python3 dashboard_integration.py
```
- Génère tous les dashboards HTML
- **Durée** : 10-30 secondes
- **Sortie attendue** :
  ```
  🎯 LUMEN - INTÉGRATION DASHBOARD AVANCÉE
  ========================================
  📊 CHARGEMENT DES DONNÉES ET DU MODÈLE
  ✅ Données chargées: 1000 lignes
  ✅ Modèle chargé: random_forest_regressor_20251022_104442.joblib
  
  🔮 GÉNÉRATION DES PRÉDICTIONS
  ✅ Prédictions générées pour 1000 échantillons
  
  🎨 CRÉATION DES VISUALISATIONS INTÉGRÉES
  ✅ Carte des zones à risque sauvegardée
  ✅ Graphique réel vs prédit sauvegardé
  ✅ Panneau des alertes actives sauvegardé
  
  ✅ INTÉGRATION DASHBOARD TERMINÉE AVEC SUCCÈS
  ```

**2.2 Vérifier les fichiers générés**
```bash
ls -lh dashboard_*.html
```
- Vérifie que les dashboards sont créés
- **Sortie attendue** :
  ```
  -rw-r--r--  1 user  staff   1.2M Oct 22 11:42 dashboard_risk_heatmap.html
  -rw-r--r--  1 user  staff   856K Oct 22 11:42 dashboard_real_vs_predicted.html
  -rw-r--r--  1 user  staff   512K Oct 22 11:42 dashboard_active_alerts.html
  ```

---

#### Étape 3 : Lancement du Serveur

**3.1 Démarrer le serveur**
```bash
python3 serveur_simple.py
```
- Lance le serveur HTTP
- **Sortie attendue** :
  ```
  🌐 LUMEN - SERVEUR UNIFIÉ
  ========================================
  🚀 Port unique: 8081
  📊 Dashboard: http://localhost:8081/
  🗺️ Carte: http://localhost:8081/dashboard_risk_heatmap.html
  📈 Prédictions: http://localhost:8081/dashboard_real_vs_predicted.html
  🚨 Alertes: http://localhost:8081/dashboard_active_alerts.html
  ========================================
  ✅ Dashboard prêt
  🌐 Serveur: http://localhost:8081
  🛑 Ctrl+C pour arrêter
  ```

**3.2 Accéder au dashboard**
- Ouvrir un navigateur
- Aller sur `http://localhost:8081/`
- **Résultat** : Dashboard LUMEN s'affiche

---

#### Étape 4 : Arrêt du Serveur

**4.1 Arrêt propre**
```bash
# Dans le terminal où le serveur tourne
Ctrl+C
```
- **Sortie attendue** :
  ```
  🛑 Serveur arrêté
  ```

**4.2 Arrêt forcé (si nécessaire)**
```bash
pkill -f python3
```
- Tue tous les processus Python

---

### Durée Totale
- **Première fois** : ~2-3 minutes (avec installation)
- **Lancements suivants** : ~30 secondes

---

## 🐳 Méthode 3 : Docker

### Avantages
- ✅ **Isolé** : Environnement conteneurisé
- ✅ **Portable** : Fonctionne partout
- ✅ **Production-ready** : Déploiement facile

### Option A : Docker Compose (Recommandé)

#### Étape 1 : Lancement avec Make

**1.1 Mode développement (avec hot-reload)**
```bash
make dev
```
- Lance Docker Compose en mode développement
- **Durée** : 30-60 secondes (première fois)
- **Sortie attendue** :
  ```
  docker compose -f compose.dev.yml up --build
  Building lumen
  ...
  Successfully built 1234567890ab
  Starting lumen_lumen_1 ... done
  Attaching to lumen_lumen_1
  lumen_1  | 🌐 LUMEN - SERVEUR UNIFIÉ
  lumen_1  | ========================================
  lumen_1  | 🚀 Port unique: 8501
  lumen_1  | ✅ Dashboard prêt
  ```

**1.2 Mode production**
```bash
make start
```
- Lance Docker Compose en mode production
- **Durée** : 30-60 secondes (première fois)

**1.3 Arrêt**
```bash
make stop
```
- Arrête les conteneurs Docker
- **Sortie attendue** :
  ```
  Stopping lumen_lumen_1 ... done
  Removing lumen_lumen_1 ... done
  ```

---

#### Étape 2 : Lancement Direct avec Docker Compose

**2.1 Mode développement**
```bash
docker compose -f compose.dev.yml up --build
```

**2.2 Mode production**
```bash
docker compose up --build
```

**2.3 Arrêt**
```bash
docker compose down
```

---

### Option B : Docker Manuel

#### Étape 1 : Construction de l'Image

**1.1 Construire l'image Docker**
```bash
docker build -t lumen-app .
```
- Construit l'image à partir du Dockerfile
- **Durée** : 2-5 minutes (première fois)
- **Sortie attendue** :
  ```
  Sending build context to Docker daemon  123.4MB
  Step 1/8 : FROM python:3.12-slim
  ...
  Successfully built 1234567890ab
  Successfully tagged lumen-app:latest
  ```

---

#### Étape 2 : Lancement du Conteneur

**2.1 Lancer le conteneur**
```bash
docker run -d -p 8501:8501 --name lumen-container lumen-app
```
- `-d` : Mode détaché (arrière-plan)
- `-p 8501:8501` : Mapping du port
- `--name lumen-container` : Nom du conteneur
- **Sortie attendue** : ID du conteneur
  ```
  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
  ```

**2.2 Vérifier que le conteneur tourne**
```bash
docker ps
```
- **Sortie attendue** :
  ```
  CONTAINER ID   IMAGE        COMMAND                  STATUS         PORTS
  a1b2c3d4e5f6   lumen-app    "streamlit run main.…"   Up 10 seconds  0.0.0.0:8501->8501/tcp
  ```

**2.3 Accéder au dashboard**
- Ouvrir `http://localhost:8501/`

---

#### Étape 3 : Arrêt et Nettoyage

**3.1 Arrêter le conteneur**
```bash
docker stop lumen-container
```
- **Sortie attendue** :
  ```
  lumen-container
  ```

**3.2 Supprimer le conteneur**
```bash
docker rm lumen-container
```
- **Sortie attendue** :
  ```
  lumen-container
  ```

**3.3 Nettoyage complet (optionnel)**
```bash
docker rmi lumen-app
```
- Supprime l'image Docker

---

### Durée Totale
- **Première fois** : ~5-10 minutes (build de l'image)
- **Lancements suivants** : ~10-30 secondes

---

## 🔍 Vérifications et Diagnostics

### Vérifier que le Serveur Fonctionne

**1. Test avec curl**
```bash
curl http://localhost:8080/
```
- **Sortie attendue** : Code HTML du dashboard

**2. Vérifier les processus Python**
```bash
ps aux | grep python3
```
- **Sortie attendue** :
  ```
  user  12345  0.5  0.3  serveur_simple.py
  ```

**3. Vérifier les ports utilisés**
```bash
lsof -i :8080
```
- **Sortie attendue** :
  ```
  COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
  python3 12345  user    3u  IPv4 0x1234      0t0  TCP *:8080 (LISTEN)
  ```

**4. Vérifier les fichiers générés**
```bash
ls -lh dashboard_*.html
```
- **Sortie attendue** : Liste des dashboards

---

## 🚨 Résolution des Problèmes

### Problème 1 : Port Déjà Utilisé

**Symptôme** :
```
❌ Port 8080 déjà utilisé
```

**Solution 1 : Utiliser le script de nettoyage**
```bash
./clean.sh
./start.sh
```

**Solution 2 : Tuer le processus manuellement**
```bash
# Trouver le processus
lsof -i :8080

# Tuer le processus
kill -9 <PID>
```

**Solution 3 : Utiliser un autre port**
```bash
# Modifier serveur_simple.py
PORT = 8082  # Au lieu de 8080
```

---

### Problème 2 : Fichiers HTML Manquants

**Symptôme** :
```
❌ Fichier dashboard_final_integration.html manquant
💡 Exécutez: python3 dashboard_integration.py
```

**Solution** :
```bash
python3 dashboard_integration.py
python3 serveur_simple.py
```

---

### Problème 3 : Dépendances Manquantes

**Symptôme** :
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution** :
```bash
pip install -r requirements.txt
```

---

### Problème 4 : Python Non Installé

**Symptôme** :
```
❌ Python 3 n'est pas installé
```

**Solution** :
```bash
# Sur macOS avec Homebrew
brew install python3

# Sur Ubuntu/Debian
sudo apt-get install python3

# Ou télécharger depuis
# https://www.python.org/downloads/
```

---

### Problème 5 : Modèle ML Non Trouvé

**Symptôme** :
```
❌ Modèle non trouvé, entraînement d'un nouveau...
```

**Solution** :
```bash
python3 ml/train_random_forest.py
python3 dashboard_integration.py
```

---

### Problème 6 : Données Manquantes

**Symptôme** :
```
❌ Données non trouvées, génération de démonstration...
```

**Solution 1 : Exécuter le pipeline complet**
```bash
python3 clean_data_controlled.py
python3 validate_data_strict.py
python3 ml/train_random_forest.py
python3 dashboard_integration.py
```

**Solution 2 : Utiliser le Makefile**
```bash
make full-pipeline
```

---

## 📊 Comparaison des Méthodes

| Critère | Script Auto | Manuel | Docker |
|---------|-------------|--------|--------|
| **Simplicité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Rapidité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Contrôle** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Production** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Débogage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Portabilité** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recommandations

### Pour le Développement
```bash
./start.sh
```
- **Rapide** et **automatique**
- Gère tout automatiquement
- Idéal pour tester rapidement

### Pour le Débogage
```bash
python3 dashboard_integration.py
python3 serveur_simple.py
```
- **Contrôle total** sur chaque étape
- Voir les erreurs en direct
- Modifier et relancer facilement

### Pour la Production
```bash
make dev
# ou
docker compose up --build
```
- **Environnement isolé**
- **Scalable** et **portable**
- Facile à déployer

---

## 📝 Checklist de Démarrage

- [ ] Python 3.7+ installé
- [ ] Fichier `requirements.txt` présent
- [ ] Dépendances installées
- [ ] Fichier `serveur_simple.py` présent
- [ ] Dashboards générés (`.html`)
- [ ] Port 8080-8090 disponible
- [ ] Navigateur web installé

---

## 🎉 Conclusion

Le processus de démarrage de LUMEN est **simple** et **flexible** :
- **Script automatique** pour un lancement rapide
- **Lancement manuel** pour plus de contrôle
- **Docker** pour la production

Choisissez la méthode qui correspond le mieux à vos besoins !
