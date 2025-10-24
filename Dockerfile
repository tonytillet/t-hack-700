FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances
RUN pip install -r requirements.txt

# Copier l'application
COPY . .

# Exposer le port
EXPOSE 8501

# Commande de démarrage avec auto-reload
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true", "--server.fileWatcherType=poll"]
