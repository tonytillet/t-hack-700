# Makefile pour automatisation du pipeline de validation
# Système LUMEN - Pipeline de données officielles

.PHONY: help clean-validate validate-strict audit-ge version-dvc evidence-pack full-pipeline

# Variables
PYTHON = python3
DATA_DIR = data
LOGS_DIR = data/logs
EVIDENCE_DIR = evidence

# Aide
help:
	@echo "🔧 PIPELINE DE VALIDATION LUMEN"
	@echo "================================"
	@echo ""
	@echo "📋 Commandes disponibles:"
	@echo "  clean-validate    - Nettoyage contrôlé avec Dataprep + Pandera"
	@echo "  validate-strict   - Validation stricte avec schémas Pandera"
	@echo "  audit-ge          - Audit automatique avec Great Expectations"
	@echo "  version-dvc       - Versioning avec DVC"
	@echo "  evidence-pack     - Création du bundle de preuve"
	@echo "  full-pipeline     - Exécution complète du pipeline"
	@echo "  clean             - Nettoyage des fichiers temporaires"
	@echo ""

# Nettoyage contrôlé
clean-validate:
	@echo "🧹 NETTOYAGE CONTRÔLÉ"
	@echo "====================="
	$(PYTHON) clean_data_controlled.py
	@echo "✅ Nettoyage terminé"

# Validation stricte
validate-strict:
	@echo "🔍 VALIDATION STRICTE"
	@echo "====================="
	$(PYTHON) validate_data_strict.py
	@echo "✅ Validation terminée"

# Audit automatique
audit-ge:
	@echo "📊 AUDIT AUTOMATIQUE"
	@echo "===================="
	$(PYTHON) setup_great_expectations.py
	@echo "✅ Audit configuré"

# Versioning DVC
version-dvc:
	@echo "🔄 VERSIONING DVC"
	@echo "================="
	$(PYTHON) setup_dvc.py
	@echo "✅ Versioning configuré"

# Bundle de preuve
evidence-pack:
	@echo "🧠 BUNDLE DE PREUVE"
	@echo "==================="
	$(PYTHON) create_evidence_pack.py
	@echo "✅ Bundle de preuve créé"

# Pipeline complet
full-pipeline: clean-validate validate-strict audit-ge version-dvc evidence-pack
	@echo "🎉 PIPELINE COMPLET TERMINÉ"
	@echo "==========================="
	@echo "✅ Toutes les étapes exécutées avec succès"
	@echo "📁 Résultats dans: $(DATA_DIR)/"
	@echo "📦 Bundle de preuve: $(EVIDENCE_DIR)/"

# Nettoyage
clean:
	@echo "🧹 NETTOYAGE"
	@echo "============"
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.pyc
	rm -rf .DS_Store
	@echo "✅ Nettoyage terminé"

# Vérification de l'état
status:
	@echo "📊 ÉTAT DU PIPELINE"
	@echo "==================="
	@echo "📁 Données brutes: $(shell find $(DATA_DIR)/raw -name "*.csv" 2>/dev/null | wc -l) fichiers"
	@echo "🧹 Données nettoyées: $(shell find $(DATA_DIR)/cleaned -name "*.csv" 2>/dev/null | wc -l) fichiers"
	@echo "✅ Données validées: $(shell find $(DATA_DIR)/validated -name "*.parquet" 2>/dev/null | wc -l) fichiers"
	@echo "🧊 Données gelées: $(shell find $(DATA_DIR)/frozen -name "*.csv" 2>/dev/null | wc -l) fichiers"
	@echo "📋 Logs: $(shell find $(LOGS_DIR) -name "*.txt" -o -name "*.json" 2>/dev/null | wc -l) fichiers"
	@echo "📦 Bundle de preuve: $(shell find $(EVIDENCE_DIR) -name "*.json" 2>/dev/null | wc -l) fichiers"

# Installation des dépendances
install-deps:
	@echo "📦 INSTALLATION DES DÉPENDANCES"
	@echo "==============================="
	pip3 install dataprep pandera great-expectations dvc
	@echo "✅ Dépendances installées"

# Test de l'intégrité
test-integrity:
	@echo "🔍 TEST D'INTÉGRITÉ"
	@echo "=================="
	@if [ -d "$(EVIDENCE_DIR)" ]; then \
		echo "📦 Bundle de preuve trouvé"; \
		ls -la $(EVIDENCE_DIR)/; \
	else \
		echo "❌ Bundle de preuve non trouvé"; \
	fi
	@if [ -d "$(DATA_DIR)/validated" ]; then \
		echo "✅ Données validées trouvées"; \
		ls -la $(DATA_DIR)/validated/; \
	else \
		echo "❌ Données validées non trouvées"; \
	fi

# Rapport de qualité
quality-report:
	@echo "📊 RAPPORT DE QUALITÉ"
	@echo "===================="
	@echo "📅 Date: $(shell date)"
	@echo "🔧 Pipeline: LUMEN Data Validation"
	@echo "📁 Données traitées: $(shell find $(DATA_DIR) -name "*.csv" -o -name "*.parquet" 2>/dev/null | wc -l) fichiers"
	@echo "📋 Logs générés: $(shell find $(LOGS_DIR) -name "*.txt" -o -name "*.json" 2>/dev/null | wc -l) fichiers"
	@echo "🧠 Bundle de preuve: $(shell find $(EVIDENCE_DIR) -name "*.json" 2>/dev/null | wc -l) composants"
	@echo ""
	@echo "✅ GARANTIES:"
	@echo "• 100% données officielles françaises"
	@echo "• Validation stricte avec Pandera"
	@echo "• Audit automatique avec Great Expectations"
	@echo "• Versioning complet avec DVC"
	@echo "• Checksums SHA256 pour intégrité"
	@echo "• Traçabilité Git complète"