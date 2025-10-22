# 🚀 LUMEN - Makefile pour Développement et Production

.PHONY: help dev build start stop restart logs status clean deploy docker local

# Variables
DOCKER_IMAGE = lumen-app
DOCKER_CONTAINER = lumen-app
PORT = 8080

# Aide par défaut
help: ## Afficher l'aide
	@echo "🚀 LUMEN - Commandes Disponibles"
	@echo "================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Commandes principales :"
	@echo "  make dev      - Démarrage rapide (Docker ou Local)"
	@echo "  make docker   - Démarrage en mode Docker"
	@echo "  make local    - Démarrage en mode Local"
	@echo "  make deploy   - Créer le package de déploiement"

# Démarrage rapide (détection automatique)
dev: ## Démarrage rapide avec détection automatique Docker/Local
	@echo "🚀 LUMEN - Démarrage Rapide"
	@echo "============================"
	@if docker info >/dev/null 2>&1; then \
		echo "🐳 Docker détecté - Démarrage en mode Docker"; \
		$(MAKE) docker; \
	else \
		echo "💻 Docker non disponible - Démarrage en mode Local"; \
		$(MAKE) local; \
	fi

# Mode Docker
docker: ## Démarrage en mode Docker
	@echo "🐳 LUMEN - Mode Docker"
	@echo "======================"
	@if ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker n'est pas démarré"; \
		echo "💡 Démarrez Docker Desktop ou le service Docker"; \
		exit 1; \
	fi
	@echo "🔨 Construction de l'image..."
	@./docker-manage.sh build
	@echo "🚀 Démarrage du conteneur..."
	@./docker-manage.sh start
	@echo ""
	@echo "✅ LUMEN Docker démarré !"
	@echo "🌐 Accès : http://localhost:$(PORT)/"
	@echo "🛑 Arrêt : make stop"

# Mode Local
local: ## Démarrage en mode Local
	@echo "💻 LUMEN - Mode Local"
	@echo "====================="
	@echo "🔧 Réparation des dashboards manquants..."
	@./fix_missing_dashboards.sh
	@echo "🚀 Démarrage du serveur local..."
	@./start.sh
	@echo ""
	@echo "✅ LUMEN Local démarré !"
	@echo "🌐 Accès : http://localhost:8081/ (ou port détecté)"
	@echo "🛑 Arrêt : make stop"

# Construction de l'image Docker
build: ## Construire l'image Docker
	@echo "🔨 Construction de l'image Docker..."
	@./docker-manage.sh build

# Démarrage du conteneur Docker
start: ## Démarrer le conteneur Docker
	@echo "🚀 Démarrage du conteneur Docker..."
	@./docker-manage.sh start

# Arrêt du conteneur Docker
stop: ## Arrêter le conteneur Docker
	@echo "🛑 Arrêt du conteneur Docker..."
	@./docker-manage.sh stop
	@echo "🛑 Arrêt des processus Python locaux..."
	@pkill -f python3 2>/dev/null || true

# Redémarrage du conteneur Docker
restart: ## Redémarrer le conteneur Docker
	@echo "🔄 Redémarrage du conteneur Docker..."
	@./docker-manage.sh restart

# Logs du conteneur Docker
logs: ## Afficher les logs du conteneur Docker
	@echo "📋 Logs du conteneur Docker..."
	@./docker-manage.sh logs

# Statut du conteneur Docker
status: ## Afficher le statut du conteneur Docker
	@echo "📊 Statut du conteneur Docker..."
	@./docker-manage.sh status

# Nettoyage complet
clean: ## Nettoyer les conteneurs et images Docker
	@echo "🧹 Nettoyage Docker..."
	@./docker-manage.sh clean
	@echo "🧹 Nettoyage des processus Python..."
	@pkill -f python3 2>/dev/null || true
	@echo "✅ Nettoyage terminé"

# Déploiement Docker
deploy-docker: ## Créer le package de déploiement Docker
	@echo "🐳 Création du package Docker..."
	@./deploy_docker.sh

# Déploiement universel
deploy: ## Créer le package de déploiement universel
	@echo "🚀 Création du package universel..."
	@./deploy_universal.sh

# Vérification des fichiers
check: ## Vérifier les fichiers essentiels
	@echo "🔍 Vérification des fichiers..."
	@./check_files.sh

# Réparation des dashboards
fix: ## Réparer les dashboards manquants
	@echo "🔧 Réparation des dashboards..."
	@./fix_missing_dashboards.sh

# Test de l'accès web
test: ## Tester l'accès web
	@echo "🌐 Test de l'accès web..."
	@curl -s http://localhost:$(PORT)/ > /dev/null && echo "✅ LUMEN accessible sur http://localhost:$(PORT)/" || echo "❌ LUMEN non accessible"

# Installation des dépendances
deps: ## Installer les dépendances Python
	@echo "📦 Installation des dépendances..."
	@pip install -r requirements.txt

# Nettoyage du projet
cleanup: ## Nettoyage agressif du projet
	@echo "🧹 Nettoyage du projet..."
	@./aggressive_cleanup.sh

# Informations sur le projet
info: ## Afficher les informations du projet
	@echo "📊 LUMEN - Informations du Projet"
	@echo "================================="
	@echo "🐳 Docker disponible : $$(docker info >/dev/null 2>&1 && echo 'Oui' || echo 'Non')"
	@echo "🐍 Python disponible : $$(python3 --version 2>/dev/null || echo 'Non installé')"
	@echo "📁 Taille du projet : $$(du -sh . | cut -f1)"
	@echo "🌐 Ports utilisés :"
	@lsof -i :8080 -i :8081 -i :8082 -i :8083 -i :8084 -i :8085 2>/dev/null || echo "   Aucun port utilisé"
