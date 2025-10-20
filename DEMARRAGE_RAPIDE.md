# ⚡ Démarrage ultra-rapide

## 🚀 Installation en 1 commande

### Étape 1 : Cloner le projet
```bash
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
```

### Étape 2 : Installer tout automatiquement
```bash
python3 install.py
```

### Étape 3 : Lancer l'application
```bash
python3 launch_app.py
```

### Étape 4 : Ouvrir dans le navigateur
Aller sur : `http://localhost:8501`

## ✅ C'est tout !

L'application va :
- ✅ Installer toutes les dépendances automatiquement
- ✅ Créer les dossiers nécessaires
- ✅ Générer des données de démonstration
- ✅ Lancer l'interface web

## 🆘 Si ça ne marche pas

### Python non trouvé
```bash
# Vérifier si Python est installé
python3 --version

# Si pas installé, aller sur https://python.org
# Télécharger Python 3.8+ et cocher "Add to PATH"
```

### Erreur de permissions (Linux/Mac)
```bash
chmod +x install.py
python3 install.py
```

### Erreur de dépendances
```bash
# Installer manuellement les dépendances principales
pip install streamlit pandas numpy scikit-learn plotly folium streamlit-folium

# Puis relancer
python3 launch_app.py
```

### Port déjà utilisé
```bash
# Tuer les processus sur le port 8501
lsof -ti:8501 | xargs kill -9

# Ou lancer sur un autre port
streamlit run app_complete.py --server.port 8502
```

## 📱 Interface

Une fois lancé, vous verrez :
- **Carte des alertes** : Visualisation des régions à risque
- **Tableau de bord** : Alertes actives et métriques
- **Protocoles d'action** : Actions recommandées
- **Analyse détaillée** : Zoom sur chaque région
- **Configuration** : Paramètres du système

## 🎯 Fonctionnalités

- 🗺️ **Carte interactive** avec alertes en temps réel
- 📊 **Tableaux de bord** professionnels
- 🚨 **Système d'alerte** automatique
- 📈 **Prédictions** 1-2 mois à l'avance
- 💰 **Calcul ROI** des actions préventives

---

**Prêt à prédire les risques de grippe ! 🚨**
