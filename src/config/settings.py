#!/usr/bin/env python3
"""
Configuration de l'application LUMEN
"""

import json
import os

class Config:
    """Gestionnaire de configuration"""

    def __init__(self, config_file='config/app_config.json'):
        self.config_file = config_file
        self._config = None
        self.load_config()

    def load_config(self):
        """Charge la configuration depuis le fichier"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement de la configuration: {e}")
                self._config = self.get_default_config()
        else:
            self._config = self.get_default_config()
            self.save_config()

    def save_config(self):
        """Sauvegarde la configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")

    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "app": {
                "name": "LUMEN - Système d'Alerte Grippe",
                "version": "2.0.0",
                "description": "Plateforme de surveillance épidémiologique prédictive"
            },
            "data": {
                "paths": {
                    "processed": "data/processed",
                    "alerts": "data/alerts",
                    "spf": "data/spf",
                    "insee": "data/insee",
                    "meteo": "data/meteo",
                    "google_trends": "data/google_trends",
                    "wikipedia": "data/wikipedia"
                },
                "update_frequency": "weekly",
                "retention_days": 365
            },
            "alerts": {
                "thresholds": {
                    "critical": 80,
                    "elevated": 60,
                    "moderate": 40,
                    "low": 20
                },
                "notification_channels": ["email", "sms", "dashboard"],
                "auto_actions": True
            },
            "ui": {
                "theme": "light",
                "language": "fr",
                "map_style": "CartoDB positron",
                "default_zoom": 6,
                "sidebar_expanded": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/lumen.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "security": {
                "api_keys_required": False,
                "session_timeout": 3600,
                "allowed_ips": []
            }
        }

    def get(self, key, default=None):
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """Définit une valeur de configuration"""
        keys = key.split('.')
        config = self._config

        # Naviguer jusqu'au dictionnaire parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Définir la valeur
        config[keys[-1]] = value
        self.save_config()

    def update(self, updates):
        """Met à jour plusieurs valeurs de configuration"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v

        deep_update(self._config, updates)
        self.save_config()

# Instance globale de configuration
config = Config()
