# 🚀 Guide de démarrage rapide

## Installation en 3 étapes

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/t-hack-700.git
cd t-hack-700
```

### 2. Installation automatique

**Sur Linux/Mac :**
```bash
./install.sh
```

**Sur Windows :**
```cmd
install.bat
```

**Installation manuelle :**
```bash
pip install -r requirements.txt
python3 scripts/collect_real_data_fixed.py
python3 scripts/fuse_data.py
python3 scripts/create_alert_system.py
```

### 3. Lancer l'application
```bash
python3 launch_app.py
```

Ouvrez votre navigateur sur : `http://localhost:8501`

## 🎯 Première utilisation

1. **Carte des alertes** : Visualisez les régions à risque
2. **Tableau de bord** : Consultez les alertes actives  
3. **Protocoles d'action** : Déclenchez les actions recommandées
4. **Analyse détaillée** : Explorez une région spécifique
5. **Configuration** : Ajustez les paramètres

## ❓ Problèmes courants

**L'application ne se lance pas :**
- Vérifiez que Python 3.9+ est installé
- Réinstallez les dépendances : `pip install -r requirements.txt`

**Données manquantes :**
- Relancez la collecte : `python3 scripts/collect_real_data_fixed.py`

**Port déjà utilisé :**
- L'application utilise le port 8501 par défaut
- Fermez les autres applications Streamlit ou changez le port

## 📞 Support

- **Documentation complète** : `README.md`
- **Issues** : [GitHub Issues](https://github.com/votre-username/t-hack-700/issues)

---

**Prêt à prédire les risques de grippe ! 🚨**
