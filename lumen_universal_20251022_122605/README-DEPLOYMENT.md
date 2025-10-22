# 🚀 LUMEN - Guide de Déploiement

## 🎯 Démarrage Rapide

```bash
./start-lumen.sh
```

## 🐳 Mode Docker (Recommandé)

Si Docker est disponible :

```bash
# Démarrage automatique
./start-lumen.sh

# Ou manuellement
./docker-manage.sh build
./docker-manage.sh start
```

**Avantages Docker :**
- ✅ Isolation complète
- ✅ Pas de conflits de ports
- ✅ Environnement reproductible
- ✅ Gestion simplifiée

## 💻 Mode Local

Si Docker n'est pas disponible :

```bash
# Démarrage automatique
./start-lumen.sh

# Ou manuellement
./fix_missing_dashboards.sh
./start.sh
```

**Avantages Local :**
- ✅ Pas de Docker requis
- ✅ Démarrage rapide
- ✅ Débogage facile

## 🌐 Accès aux Dashboards

Une fois démarré, LUMEN est accessible sur :

- **Menu Principal :** http://localhost:8080/ (Docker) ou http://localhost:8081/ (Local)
- **Bulletin Public :** /bulletin_lumen.html
- **Vue Pédagogique :** /dashboard_pedagogique.html
- **Carte des Risques :** /dashboard_risk_heatmap.html
- **Prédictions :** /dashboard_real_vs_predicted.html
- **Alertes Actives :** /dashboard_active_alerts.html

## 🔧 Commandes de Gestion

### Docker :
```bash
./docker-manage.sh start    # Démarrer
./docker-manage.sh stop     # Arrêter
./docker-manage.sh restart  # Redémarrer
./docker-manage.sh logs     # Voir les logs
./docker-manage.sh status   # Voir le statut
```

### Local :
```bash
./start.sh                  # Démarrer
pkill -f python3           # Arrêter
./fix_missing_dashboards.sh # Réparer
```

## 🎉 Résultat

**LUMEN fonctionne parfaitement dans les deux modes !** 🚀
