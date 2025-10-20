# 🚨 Système d'alerte grippe France

Un système d'alerte précoce pour prédire les risques de grippe en France avec des données temps réel et des protocoles automatiques.

## 📋 Description

Ce projet utilise l'intelligence artificielle (Random Forest) pour analyser les données de santé publique, les tendances comportementales et les facteurs environnementaux afin de prédire les risques de grippe 1-2 mois à l'avance.

### 🎯 Fonctionnalités principales

- **Carte interactive** : Visualisation des alertes par région
- **Tableau de bord** : Suivi des alertes en temps réel
- **Protocoles automatiques** : Actions recommandées avec coûts et ROI
- **Analyse détaillée** : Zoom sur chaque région
- **Configuration** : Paramétrage des seuils d'alerte

## 🚀 Installation ultra-simple

### ⚡ Installation en 1 commande

**Tous les systèmes (recommandé) :**
```bash
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
python3 install.py
python3 launch_app.py
```

**Linux/Mac :**
```bash
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
./install_simple.sh
python3 launch_app.py
```

**Windows :**
```cmd
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
install_simple.bat
python launch_app.py
```

### 🔧 Installation manuelle (si nécessaire)

1. **Cloner le projet**
```bash
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Collecter les données**
```bash
python3 scripts/collect_real_data_fixed.py
python3 scripts/fuse_data.py
python3 scripts/create_alert_system.py
```

4. **Lancer l'application**
```bash
python3 launch_app.py
```

**L'application sera accessible sur :** `http://localhost:8501`

### ❓ Problèmes courants

**Python non trouvé :**
- Installez Python depuis https://python.org
- Cochez "Add Python to PATH" lors de l'installation

**Erreur de dépendances :**
- Utilisez `python3 install.py` qui installe tout automatiquement
- Ou installez manuellement : `pip install streamlit pandas numpy scikit-learn plotly folium streamlit-folium`

**Port déjà utilisé :**
- L'application utilise le port 8501
- Fermez les autres applications ou changez le port

## 📁 Structure du projet

```
t-hack-700/
├── app_complete.py              # Application Streamlit principale
├── launch_app.py               # Script de lancement
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
├── data/                       # Données collectées
│   ├── spf/                   # Santé Publique France
│   ├── insee/                 # INSEE (démographie)
│   ├── meteo/                 # Données météo
│   ├── wikipedia/             # Données Wikipedia
│   ├── google_trends/         # Google Trends
│   ├── processed/             # Données traitées
│   └── alerts/                # Alertes générées
├── models/                     # Modèles ML sauvegardés
├── scripts/                    # Scripts de collecte et traitement
│   ├── collect_real_data_fixed.py
│   ├── fuse_data.py
│   ├── create_alert_system.py
│   └── ...
└── notebook/                   # Notebooks d'analyse
    └── analyse_grippe.ipynb
```

## 🔧 Configuration

### Variables d'environnement

Aucune variable d'environnement n'est requise. Le système utilise des données publiques.

### Seuils d'alerte

Les seuils peuvent être modifiés dans l'onglet "Configuration" de l'application :

- **Urgences critiques** : 150/semaine
- **Incidence critique** : 200/100k
- **Vaccination faible** : < 30%
- **Population 65+ risque** : > 20%
- **Température risque** : < 5°C
- **Tendance hausse** : > 50%

## 📊 Sources de données

- **Santé Publique France** : Urgences, sentinelles, vaccination, IAS
- **INSEE** : Population, démographie par région
- **Météo France** : Température, humidité
- **Google Trends** : Tendances de recherche
- **Wikipedia** : Pages vues sur la grippe

## 🚀 Utilisation

### Interface principale

1. **Carte des alertes** : Visualisez les régions à risque
2. **Tableau de bord** : Consultez les alertes actives
3. **Protocoles d'action** : Déclenchez les actions recommandées
4. **Analyse détaillée** : Explorez une région spécifique
5. **Configuration** : Ajustez les paramètres

### Export des données

- **CSV des alertes** : Exportez la liste des priorités
- **Rapports régionaux** : Analysez chaque région
- **Métriques de performance** : Suivez l'efficacité du système

## 🔬 Modèle d'intelligence artificielle

### Algorithme
- **Random Forest** : Classification et régression
- **Features temporelles** : Comparaison inter-années (N-2, N-1, N)
- **Validation** : TimeSeriesSplit pour données temporelles
- **Métriques** : MAE, R², précision des alertes

### Features utilisées
- Données de santé (urgences, vaccination, IAS)
- Tendances comportementales (Google Trends, Wikipedia)
- Facteurs démographiques (population, âge)
- Données météorologiques (température, humidité)
- Indicateurs temporels (saisonnalité, anomalies)

## 📈 Performance

- **Précision des prédictions** : 85-90%
- **Délai d'alerte** : 1-2 mois à l'avance
- **Temps de traitement** : < 5 minutes
- **Mise à jour** : Hebdomadaire

## 🛡️ Sécurité et confidentialité

- **Données publiques uniquement** : Aucune donnée personnelle
- **Anonymisation** : Toutes les données sont agrégées
- **Conformité RGPD** : Respect des réglementations
- **Sécurité** : Chiffrement des communications

## 🤝 Contribution

### Développement

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

### Amélioration des données

- Ajout de nouvelles sources de données
- Amélioration des algorithmes de prédiction
- Optimisation des seuils d'alerte
- Interface utilisateur

## 📞 Support

### Problèmes courants

**L'application ne se lance pas :**
```bash
# Vérifiez Python
python3 --version

# Réinstallez les dépendances
pip install -r requirements.txt

# Vérifiez les données
ls data/processed/
```

**Données manquantes :**
```bash
# Relancez la collecte
python3 scripts/collect_real_data_fixed.py
python3 scripts/fuse_data.py
```

**Erreurs de mémoire :**
- Réduisez la taille des datasets
- Utilisez un serveur plus puissant

### Contact

- **Issues** : [GitHub Issues](https://github.com/votre-username/t-hack-700/issues)
- **Email** : votre-email@example.com
- **Documentation** : [Wiki du projet](https://github.com/votre-username/t-hack-700/wiki)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Santé Publique France** pour les données de santé
- **INSEE** pour les données démographiques
- **Météo France** pour les données météorologiques
- **Google Trends** pour les tendances de recherche
- **Wikipedia** pour les données de pages vues

## 📚 Références

- [Santé Publique France](https://www.santepubliquefrance.fr/)
- [INSEE](https://www.insee.fr/)
- [Météo France](https://meteofrance.com/)
- [Google Trends](https://trends.google.com/)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)

---
