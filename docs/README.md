# 📚 Documentation LUMEN

Bienvenue dans la documentation complète du projet LUMEN Enhanced !

## 📖 Guides Disponibles

### 🤖 [Pipeline Machine Learning](PIPELINE_ML.md)
Guide complet du pipeline ML de bout en bout - **NOUVEAU** ⭐

**Contenu** :
- Vue d'ensemble du pipeline en 7 étapes
- Ordre d'exécution des scripts
- Explication détaillée de chaque étape
- Flux de données et transformations
- Commandes Makefile
- Exemples pratiques
- Durées d'exécution

---

### 🚀 [Processus de Démarrage](PROCESSUS_DEMARRAGE.md)
Guide complet pour lancer le projet LUMEN avec 3 méthodes différentes :
- **Script automatique** (`start.sh`) - Recommandé ✅
- **Lancement manuel** (commandes Python)
- **Docker** (conteneurisation)

**Contenu** :
- Vue d'ensemble des méthodes
- Processus détaillé étape par étape
- Vérifications et diagnostics
- Résolution des problèmes courants
- Comparaison des méthodes

---

### 📜 [Documentation des Scripts](SCRIPTS.md)
Documentation détaillée de tous les scripts du projet (Shell et Python).

**Scripts Shell** :
- `start.sh` - Lancement automatique
- `clean.sh` - Nettoyage du projet
- `monitoring/daily_monitoring.sh` - Monitoring quotidien
- `monitoring/weekly_retrain.sh` - Retrain hebdomadaire

**Scripts Python** :
- `serveur_simple.py` - Serveur HTTP unifié
- `dashboard_integration.py` - Génération des dashboards
- `clean_data_controlled.py` - Nettoyage des données
- `validate_data_strict.py` - Validation des données
- `monitoring_auto_retrain.py` - Auto-retrain et monitoring
- `explicabilite_shap.py` - Explicabilité SHAP
- `generate_meaningful_data.py` - Données synthétiques
- `main.py` - Application Streamlit

**Contenu** :
- Description de chaque script
- Fonctionnalités détaillées
- Code source commenté
- Utilisation et exemples
- Dépendances entre scripts
- Bonnes pratiques

---

## 🎯 Par Où Commencer ?

### Vous voulez lancer le projet rapidement ?
→ Consultez **[Processus de Démarrage](PROCESSUS_DEMARRAGE.md)** - Section "Méthode 1"

### Vous voulez comprendre comment fonctionne un script ?
→ Consultez **[Documentation des Scripts](SCRIPTS.md)**

### Vous rencontrez un problème ?
→ Consultez **[Processus de Démarrage](PROCESSUS_DEMARRAGE.md)** - Section "Résolution des Problèmes"

---

## 📊 Structure de la Documentation

```
docs/
├── README.md                    # Ce fichier (index)
├── PROCESSUS_DEMARRAGE.md      # Guide de démarrage complet
└── SCRIPTS.md                   # Documentation des scripts
```

---

## 🔗 Liens Utiles

- **README principal** : [../README.md](../README.md)
- **Makefile** : [../Makefile](../Makefile)
- **Requirements** : [../requirements.txt](../requirements.txt)

---

## 💡 Conseils

1. **Toujours utiliser `start.sh`** pour lancer le projet (gère tout automatiquement)
2. **Exécuter `clean.sh`** avant de relancer si problèmes de port
3. **Vérifier les logs** dans `monitoring/logs/` en cas d'erreur
4. **Régénérer les dashboards** avec `dashboard_integration.py` si fichiers manquants

---

## 📞 Support

Pour toute question ou problème :
1. Consultez la section "Résolution des Problèmes" dans [PROCESSUS_DEMARRAGE.md](PROCESSUS_DEMARRAGE.md)
2. Vérifiez les logs dans `monitoring/logs/`
3. Exécutez `./clean.sh` puis `./start.sh`

---

**🧠 LUMEN Enhanced - Documentation Complète**  
*Tout ce dont vous avez besoin pour comprendre et utiliser LUMEN*
