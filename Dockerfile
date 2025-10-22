# 🐳 Dockerfile pour LUMEN - Système de Surveillance Épidémiologique

FROM python:3.9-slim

# Métadonnées
LABEL maintainer="LUMEN Team"
LABEL description="Système de surveillance épidémiologique intelligente"
LABEL version="1.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LUMEN_PORT=8080

# Créer le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers essentiels
COPY serveur_simple.py .
COPY start.sh .
COPY check_files.sh .
COPY fix_missing_dashboards.sh .
COPY generate_all_dashboards.py .
COPY dashboard_integration.py .

# Copier les dashboards HTML
COPY *.html .

# Copier les dossiers de données (sans les gros fichiers)
COPY data/ data/
COPY models/ models/
COPY ml/ ml/
COPY monitoring/ monitoring/

# Rendre les scripts exécutables
RUN chmod +x *.sh

# Script de démarrage
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Créer un utilisateur non-root
RUN useradd -m -u 1000 lumen && chown -R lumen:lumen /app
USER lumen

# Exposer le port
EXPOSE 8080

# Point d'entrée
ENTRYPOINT ["./docker-entrypoint.sh"]