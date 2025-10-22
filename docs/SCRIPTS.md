# 📜 LUMEN - Documentation des Scripts

## 📋 Table des Matières
- [Scripts Shell](#scripts-shell)
- [Scripts Python](#scripts-python)
- [Scripts de Monitoring](#scripts-de-monitoring)

---

## 🐚 Scripts Shell

### `start.sh` - Script de Lancement Automatique

**Emplacement** : `/start.sh`

**Description** : Script principal pour lancer automatiquement le système LUMEN avec toutes les vérifications nécessaires.

**Fonctionnalités** :
1. ✅ Vérification de Python 3
2. 📦 Installation automatique des dépendances
3. 🛑 Arrêt des processus existants
4. 🔍 Détection automatique d'un port libre
5. 🚀 Lancement du serveur
6. 🌐 Ouverture automatique du navigateur
7. 📊 Affichage des URLs disponibles

**Utilisation** :
```bash
./start.sh
```

**Processus détaillé** :

1. **Vérification de Python** (lignes 8-13)
   ```bash
   if ! command -v python3 &> /dev/null; then
       echo "❌ Python 3 n'est pas installé"
       exit 1
   fi
   ```
   - Vérifie que Python 3 est installé sur le système
   - Affiche un message d'erreur si absent

2. **Vérification des dépendances** (lignes 15-22)
   ```bash
   if [ ! -f "requirements.txt" ]; then
       echo "❌ Fichier requirements.txt manquant"
       exit 1
   fi
   pip install -r requirements.txt > /dev/null 2>&1
   ```
   - Vérifie la présence du fichier `requirements.txt`
   - Installe silencieusement toutes les dépendances Python

3. **Arrêt des processus existants** (lignes 30-35)
   ```bash
   pkill -f python3 2>/dev/null || true
   sleep 2
   ```
   - Tue tous les processus Python en cours
   - Attend 2 secondes pour libérer les ressources

4. **Détection d'un port libre** (lignes 37-41)
   ```bash
   PORT=8081
   while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
       PORT=$((PORT + 1))
   done
   ```
   - Commence par le port 8081
   - Incrémente jusqu'à trouver un port disponible
   - Utilise `lsof` pour vérifier l'occupation des ports

5. **Modification dynamique du port** (ligne 46)
   ```bash
   sed -i.tmp "s/PORT = [0-9]*/PORT = $PORT/" serveur_simple.py
   ```
   - Modifie le fichier `serveur_simple.py` avec le port trouvé
   - Crée une sauvegarde `.tmp` avant modification

6. **Lancement du serveur** (lignes 48-52)
   ```bash
   python3 serveur_simple.py &
   sleep 3
   ```
   - Lance le serveur en arrière-plan (`&`)
   - Attend 3 secondes pour le démarrage

7. **Vérification du démarrage** (lignes 54-86)
   ```bash
   if curl -s http://localhost:$PORT/ > /dev/null; then
       echo "✅ Serveur LUMEN lancé avec succès !"
   else
       echo "❌ Erreur lors du lancement du serveur"
       exit 1
   fi
   ```
   - Teste la connexion au serveur avec `curl`
   - Affiche les URLs disponibles si succès

8. **Ouverture automatique du navigateur** (lignes 71-78)
   ```bash
   if command -v open &> /dev/null; then
       open http://localhost:$PORT/
   elif command -v xdg-open &> /dev/null; then
       xdg-open http://localhost:$PORT/
   fi
   ```
   - Utilise `open` sur macOS
   - Utilise `xdg-open` sur Linux
   - Ouvre automatiquement le navigateur par défaut

9. **Nettoyage** (ligne 89)
   ```bash
   rm -f serveur_simple.py.tmp
   ```
   - Supprime le fichier temporaire créé par `sed`

**Sortie attendue** :
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
```

---

### `clean.sh` - Script de Nettoyage

**Emplacement** : `/clean.sh`

**Description** : Script pour nettoyer le projet et libérer les ressources.

**Fonctionnalités** :
1. 🛑 Arrêt de tous les processus Python
2. 🔓 Libération des ports 8080-8090
3. 🗑️ Suppression des fichiers temporaires
4. 🧹 Nettoyage du cache Python

**Utilisation** :
```bash
./clean.sh
```

**Processus détaillé** :

1. **Arrêt des processus Python** (ligne 9)
   ```bash
   pkill -f python3 2>/dev/null || true
   ```
   - Tue tous les processus Python actifs
   - Ignore les erreurs si aucun processus n'est trouvé

2. **Libération des ports** (ligne 13)
   ```bash
   lsof -ti:8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090 | xargs kill -9 2>/dev/null || true
   ```
   - Liste tous les processus utilisant les ports 8080-8090
   - Force leur arrêt avec `kill -9`

3. **Suppression des fichiers temporaires** (lignes 17-20)
   ```bash
   rm -f *.bak *.tmp *.log
   rm -f serveur_simple.py.bak serveur_simple.py.tmp
   rm -f __pycache__/*.pyc 2>/dev/null || true
   rm -rf __pycache__/ 2>/dev/null || true
   ```
   - Supprime les fichiers de sauvegarde (`.bak`, `.tmp`)
   - Supprime les logs
   - Nettoie le cache Python

**Sortie attendue** :
```
🧹 Nettoyage du projet LUMEN...
================================
🛑 Arrêt des processus Python...
🔓 Libération des ports...
🗑️ Suppression des fichiers temporaires...
✅ Nettoyage terminé !

🚀 Vous pouvez maintenant lancer le projet avec :
   ./start.sh

🌐 Ou directement :
   python3 serveur_simple.py
```

---

## 🐍 Scripts Python

### `serveur_simple.py` - Serveur HTTP Unifié

**Emplacement** : `/serveur_simple.py`

**Description** : Serveur HTTP simple qui sert tous les dashboards HTML sur un seul port.

**Fonctionnalités** :
1. 🌐 Serveur HTTP sur un port unique
2. 🔄 Redirection automatique vers le menu principal
3. ✅ Vérification des fichiers essentiels
4. 📊 Affichage des URLs disponibles

**Classe principale** : `LUMENHandler`
```python
class LUMENHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Redirection vers le menu principal
        if self.path == '/':
            self.path = '/index.html'
        
        # Servir le fichier
        return super().do_GET()
```

**Utilisation** :
```bash
python3 serveur_simple.py
```

**Configuration** :
- **Port par défaut** : 8081 (modifiable dans le code ligne 22)
- **Fichiers requis** :
  - `dashboard_final_integration.html` (menu principal)
  - `dashboard_risk_heatmap.html` (carte)
  - `dashboard_real_vs_predicted.html` (prédictions)
  - `dashboard_active_alerts.html` (alertes)

**Gestion des erreurs** :
- **Port occupé** : Affiche un message avec la commande pour libérer le port
- **Fichiers manquants** : Suggère d'exécuter `dashboard_integration.py`

---

### `dashboard_integration.py` - Génération des Dashboards

**Emplacement** : `/dashboard_integration.py`

**Description** : Génère tous les dashboards HTML interactifs avec Plotly.

**Fonctionnalités** :
1. 📊 Chargement des données et du modèle ML
2. 🔮 Génération des prédictions
3. 🗺️ Création de la carte des zones à risque
4. 📈 Création des graphiques réel vs prédit
5. 🚨 Création du panneau des alertes actives
6. 📋 Génération d'un rapport d'intégrité

**Classe principale** : `LUMENDashboardIntegration`

**Méthodes importantes** :

1. **`load_data_and_model()`**
   - Charge les données depuis `data/processed/dataset.parquet`
   - Charge le modèle ML le plus récent depuis `models/`
   - Génère des données de démonstration si nécessaire

2. **`generate_predictions()`**
   - Génère les prédictions avec le modèle ML
   - Calcule les niveaux d'alerte (VERT, JAUNE, ORANGE, ROUGE)
   - Sauvegarde les prédictions

3. **`create_risk_heatmap()`**
   - Crée une carte interactive des zones à risque
   - Utilise Plotly pour la visualisation géographique
   - Sauvegarde dans `dashboard_risk_heatmap.html`

4. **`create_real_vs_predicted()`**
   - Crée des graphiques comparant réel et prédit
   - Affiche les tendances temporelles
   - Sauvegarde dans `dashboard_real_vs_predicted.html`

5. **`create_active_alerts()`**
   - Crée un panneau des alertes actives
   - Liste les départements en alerte
   - Sauvegarde dans `dashboard_active_alerts.html`

**Utilisation** :
```bash
python3 dashboard_integration.py
```

**Fichiers générés** :
- `dashboard_risk_heatmap.html` (carte des zones à risque)
- `dashboard_real_vs_predicted.html` (graphiques)
- `dashboard_active_alerts.html` (alertes)
- `monitoring/logs/integrity_report_YYYYMMDD_HHMMSS.json` (rapport)

**Sortie attendue** :
```
🎯 LUMEN - INTÉGRATION DASHBOARD AVANCÉE
========================================
📊 CHARGEMENT DES DONNÉES ET DU MODÈLE
========================================
✅ Données chargées: 1000 lignes
✅ Modèle chargé: random_forest_regressor_20251022_104442.joblib

🔮 GÉNÉRATION DES PRÉDICTIONS
========================================
✅ Prédictions générées pour 1000 échantillons
📊 Niveaux d'alerte: {'ROUGE': 1000}

🎨 CRÉATION DES VISUALISATIONS INTÉGRÉES
========================================
✅ Carte des zones à risque sauvegardée
✅ Graphique réel vs prédit sauvegardé
✅ Panneau des alertes actives sauvegardé
📊 6 alertes actives détectées

✅ INTÉGRATION DASHBOARD TERMINÉE AVEC SUCCÈS
```

---

### `clean_data_controlled.py` - Nettoyage des Données

**Emplacement** : `/clean_data_controlled.py`

**Description** : Nettoyage contrôlé et standardisation des données officielles.

**Fonctionnalités** :
1. 📂 Lecture des données brutes depuis `data/raw/`
2. 🧹 Nettoyage avec Dataprep et Pandera
3. 🔐 Calcul des checksums SHA256
4. 📋 Traçabilité des sources
5. 💾 Sauvegarde dans `data/cleaned/`

**Classe principale** : `ControlledDataCleaner`

**Méthodes importantes** :

1. **`calculate_sha256(filepath)`**
   - Calcule le checksum SHA256 d'un fichier
   - Garantit l'intégrité des données

2. **`get_source_traceability(filename)`**
   - Récupère la source depuis le nom de fichier
   - Maintient la traçabilité des données

3. **`clean_dataframe(df, filename)`**
   - Nettoie les en-têtes avec Dataprep
   - Supprime les doublons
   - Gère les valeurs manquantes
   - Normalise les formats

**Utilisation** :
```bash
python3 clean_data_controlled.py
```

**Fichiers d'entrée** :
- `data/raw/*.csv`
- `data/raw/*.json`
- `data/frozen/*` (données gelées)

**Fichiers de sortie** :
- `data/cleaned/*.csv` (données nettoyées)
- `data/cleaned/cleaning_report_YYYYMMDD_HHMMSS.json` (rapport)

---

### `validate_data_strict.py` - Validation des Données

**Emplacement** : `/validate_data_strict.py`

**Description** : Validation stricte des données nettoyées avec Pandera.

**Fonctionnalités** :
1. ✅ Validation des types de données
2. 🔍 Vérification des plages de valeurs
3. 📅 Vérification de la cohérence temporelle
4. 🚨 Détection des anomalies
5. 📋 Génération d'un rapport de validation

**Utilisation** :
```bash
python3 validate_data_strict.py
```

**Fichiers d'entrée** :
- `data/cleaned/*.csv`

**Fichiers de sortie** :
- `data/validated/*.csv` (données validées)
- `reports/validation_report.json` (rapport)

---

### `monitoring_auto_retrain.py` - Auto-Retrain et Monitoring

**Emplacement** : `/monitoring_auto_retrain.py`

**Description** : Système de monitoring automatique avec retrain et alertes.

**Fonctionnalités** :
1. 📊 Vérification de nouvelles données
2. 🤖 Ré-entraînement automatique du modèle
3. 📈 Comparaison des performances
4. 🚨 Génération d'alertes
5. 📧 Envoi de notifications (email)

**Classe principale** : `LUMENMonitoring`

**Méthodes importantes** :

1. **`check_new_data()`**
   - Vérifie la disponibilité de nouvelles données
   - Compare avec la dernière date d'entraînement

2. **`retrain_model()`**
   - Charge les nouvelles données
   - Ré-entraîne le modèle Random Forest
   - Sauvegarde le nouveau modèle

3. **`compare_performance()`**
   - Compare les métriques (R², MAE)
   - Décide si le nouveau modèle est meilleur
   - Génère des alertes si dégradation

4. **`send_alert()`**
   - Envoie des notifications par email
   - Enregistre dans les logs

**Utilisation** :
```bash
python3 monitoring_auto_retrain.py
```

**Configuration** :
- Fichier : `monitoring/config.json`
- Seuils de performance configurables

**Fichiers générés** :
- `models/random_forest_regressor_YYYYMMDD_HHMMSS.joblib` (nouveau modèle)
- `monitoring/logs/metrics_YYYYMMDD_HHMMSS.json` (métriques)
- `monitoring/logs/retrain_YYYYMMDD.log` (logs)

---

### `explicabilite_shap.py` - Explicabilité SHAP

**Emplacement** : `/explicabilite_shap.py`

**Description** : Génération des plots SHAP pour l'explicabilité du modèle ML.

**Fonctionnalités** :
1. 📊 Calcul des valeurs SHAP
2. 📈 Génération de 15 plots différents
3. 💾 Sauvegarde dans `explicabilite/`

**Plots générés** :
- Summary plot
- Waterfall plot
- Force plot
- Dependence plots
- Feature importance

**Utilisation** :
```bash
python3 explicabilite_shap.py
```

---

### `generate_meaningful_data.py` - Génération de Données Synthétiques

**Emplacement** : `/generate_meaningful_data.py`

**Description** : Génère des données synthétiques réalistes pour les tests.

**Fonctionnalités** :
1. 🎲 Génération de données basées sur des patterns réels
2. 📅 Simulation de la saisonnalité de la grippe
3. 🗺️ Données pour toutes les régions françaises

**Utilisation** :
```bash
python3 generate_meaningful_data.py
```

---

## 🔄 Scripts de Monitoring

### `monitoring/daily_monitoring.sh` - Monitoring Quotidien

**Emplacement** : `/monitoring/daily_monitoring.sh`

**Description** : Script exécuté quotidiennement pour surveiller le système.

**Fonctionnalités** :
1. 📊 Exécution du monitoring automatique
2. 🗑️ Nettoyage des logs anciens (> 30 jours)
3. 📝 Enregistrement dans les logs

**Utilisation** :
```bash
bash monitoring/daily_monitoring.sh
```

**Configuration Crontab** :
```bash
# Monitoring quotidien à 6h00
0 6 * * * /path/to/monitoring/daily_monitoring.sh
```

**Processus** :
1. Change le répertoire de travail
2. Exécute `monitoring_auto_retrain.py`
3. Redirige la sortie vers `monitoring/logs/daily_monitoring.log`
4. Supprime les logs de plus de 30 jours

---

### `monitoring/weekly_retrain.sh` - Retrain Hebdomadaire

**Emplacement** : `/monitoring/weekly_retrain.sh`

**Description** : Script exécuté hebdomadairement pour ré-entraîner le modèle.

**Fonctionnalités** :
1. 🤖 Ré-entraînement complet du modèle
2. 📊 Génération d'un rapport de performance
3. 📝 Enregistrement dans les logs

**Utilisation** :
```bash
bash monitoring/weekly_retrain.sh
```

**Configuration Crontab** :
```bash
# Retrain hebdomadaire tous les dimanches à 2h00
0 2 * * 0 /path/to/monitoring/weekly_retrain.sh
```

**Processus** :
1. Change le répertoire de travail
2. Enregistre l'heure de début
3. Exécute `monitoring_auto_retrain.py`
4. Génère un rapport avec les métriques (R², MAE)
5. Enregistre l'heure de fin
6. Tout est sauvegardé dans `monitoring/logs/weekly_retrain.log`

**Rapport généré** :
```
📊 Rapport hebdomadaire LUMEN - 22/10/2025
R² Score: 0.9710
MAE: 5.0800
Modèle: models/random_forest_regressor_20251022_104442.joblib
```

---

## 📊 Résumé des Scripts

### Scripts Shell (3)
| Script | Fonction | Fréquence |
|--------|----------|-----------|
| `start.sh` | Lancement automatique | Manuel |
| `clean.sh` | Nettoyage du projet | Manuel |
| `monitoring/daily_monitoring.sh` | Monitoring quotidien | Automatique (cron) |
| `monitoring/weekly_retrain.sh` | Retrain hebdomadaire | Automatique (cron) |

### Scripts Python (8)
| Script | Fonction | Utilisation |
|--------|----------|-------------|
| `serveur_simple.py` | Serveur HTTP | Automatique |
| `dashboard_integration.py` | Génération dashboards | Avant lancement |
| `clean_data_controlled.py` | Nettoyage données | Pipeline |
| `validate_data_strict.py` | Validation données | Pipeline |
| `monitoring_auto_retrain.py` | Auto-retrain | Automatique |
| `explicabilite_shap.py` | Plots SHAP | Optionnel |
| `generate_meaningful_data.py` | Données synthétiques | Tests |
| `main.py` | Application Streamlit | Alternatif |

---

## 🔗 Dépendances entre Scripts

```
start.sh
  ├── Vérifie Python
  ├── Installe requirements.txt
  └── Lance serveur_simple.py
      └── Sert les fichiers HTML générés par dashboard_integration.py

dashboard_integration.py
  ├── Charge data/processed/dataset.parquet
  ├── Charge models/*.joblib
  └── Génère *.html

monitoring_auto_retrain.py
  ├── Charge data/processed/dataset.parquet
  ├── Ré-entraîne le modèle
  └── Sauvegarde models/*.joblib

clean_data_controlled.py
  ├── Lit data/raw/*.csv
  └── Écrit data/cleaned/*.csv

validate_data_strict.py
  ├── Lit data/cleaned/*.csv
  └── Écrit data/validated/*.csv
```

---

## 💡 Bonnes Pratiques

1. **Toujours utiliser `start.sh`** pour lancer le projet (gère tout automatiquement)
2. **Exécuter `clean.sh`** avant de relancer si problèmes de port
3. **Vérifier les logs** dans `monitoring/logs/` en cas d'erreur
4. **Régénérer les dashboards** avec `dashboard_integration.py` si fichiers manquants
5. **Configurer le crontab** pour le monitoring automatique en production
