# Éthique et Confidentialité des Données

## Vue d'ensemble

LUMEN traite des données de santé publique sensibles. Ce document détaille les principes éthiques, les mesures de protection de la vie privée et la conformité réglementaire du projet.

## Principes Éthiques Fondamentaux

### 1. Transparence
- **Ouverture du code source** : Tous les scripts de traitement sont open source
- **Documentation complète** : Pipeline et méthodologie entièrement documentés
- **Traçabilité** : Logs détaillés de toutes les transformations de données
- **Reproductibilité** : DVC assure la reproductibilité des analyses

### 2. Finalité Légitime
- **Objectif** : Prédiction des pics d'affluence aux urgences pour optimiser les ressources hospitalières
- **Bénéfice public** : Amélioration de la prise en charge des patients
- **Usage restreint** : Pas d'utilisation commerciale ou d'exploitation individuelle

### 3. Minimisation des Données
- **Données agrégées uniquement** : Pas de données individuelles, seulement des statistiques par département/région
- **Période limitée** : Conservation uniquement des données nécessaires à l'entraînement
- **Suppression automatique** : Les données brutes obsolètes sont purgées périodiquement

### 4. Équité et Non-discrimination
- **Pas de biais géographiques** : Modèle entraîné sur toutes les régions françaises
- **Validation équitable** : Métriques calculées par département pour détecter les biais
- **Accessibilité** : Dashboard accessible à tous les professionnels de santé autorisés

## Sources de Données et Confidentialité

### 1. Données d'Urgences Hospitalières (data.gouv.fr)

**Source** : [data.gouv.fr - Tensions hospitalières](https://www.data.gouv.fr/fr/datasets/)

**Nature des données** :
- Comptages agrégés par département et région
- Pas de données individuelles (pas de noms, adresses, diagnostics individuels)
- Niveau de granularité : département × jour

**Statut légal** :
- Données publiques (Open Data)
- Licence Ouverte 2.0 (Etalab)
- Réutilisation libre avec mention de la source

**Mesures de protection** :
- Agrégation au niveau département (k-anonymat implicite)
- Seuils de publication : comptages < 5 non publiés par data.gouv.fr
- Pas de croisement avec d'autres sources nominatives

**Conformité RGPD** :
- Hors champ RGPD : données agrégées sans identification possible
- Pas de transfert hors UE
- Pas de profilage individuel

### 2. Données Météorologiques (Open Meteo API)

**Source** : API météo publiques (Open-Meteo, Météo France Data)

**Nature des données** :
- Température, humidité, pression atmosphérique
- Granularité : station météo (ville/département)
- Données historiques et temps réel

**Statut légal** :
- Données environnementales publiques
- APIs gratuites et open source
- Aucune donnée personnelle

**Usage** :
- Corrélation avec les afflux d'urgences (canicules, vagues de froid)
- Variables explicatives pour le modèle prédictif

### 3. Données Wikipedia (Métadonnées)

**Source** : Wikipedia API

**Nature des données** :
- Métadonnées sur les articles liés à la santé publique
- Consultations de pages (agrégées)
- Aucune donnée utilisateur

**Statut légal** :
- Contenu sous licence CC BY-SA
- API publique

**Usage** :
- Indicateur indirect de l'intérêt du public pour les sujets de santé
- Variable exploratoire (faible poids dans le modèle actuel)

## Architecture de Sécurité

### Stockage des Données

```
data/
├── raw/                    # Données brutes (DVC, non commité Git)
│   └── .gitignore          # Exclusion des fichiers sensibles
├── processed/              # Données nettoyées (agrégées)
├── features/               # Features anonymisées
└── artifacts/              # Modèles (pas de données personnelles)
```

**Mesures** :
- `.gitignore` : Données brutes exclues du versioning Git
- DVC : Stockage séparé avec contrôle d'accès
- Chiffrement : Stockage distant chiffré (si applicable)
- Backups : Sauvegarde régulière avec rétention limitée

### Accès et Authentification

**Contrôle d'accès** :
- Code source : Public (GitHub)
- Données brutes : Accès restreint aux contributeurs autorisés
- DVC remote : Authentification par clé SSH/token
- Dashboard : Authentification à implémenter (Streamlit Auth)

**Logs d'audit** :
- Traçabilité des modifications de données (`clean_data.log`)
- Git history pour les changements de code
- DVC tracking pour les versions de données

### Transmission des Données

**Protocoles** :
- HTTPS obligatoire pour toutes les APIs
- TLS 1.3 pour les connexions réseau
- Pas de transmission de données sensibles hors infrastructure autorisée

## Conformité Réglementaire

### RGPD (Règlement Général sur la Protection des Données)

**Applicabilité** : Limitée (données agrégées, pas de personnes identifiables)

**Droits des personnes** (non applicables car pas de données individuelles) :
- Droit d'accès : N/A (données agrégées)
- Droit de rectification : N/A
- Droit à l'effacement : N/A
- Droit à la portabilité : N/A

**Base légale** (si applicable) :
- Intérêt légitime : Recherche en santé publique
- Mission d'intérêt public : Optimisation du système de santé

**Durée de conservation** :
- Données d'entraînement : 5 ans maximum
- Modèles : Durée de vie du projet
- Logs : 1 an

### Loi Informatique et Libertés (LIL)

**Déclaration CNIL** : Non requise (données anonymes et publiques)

**Si extension future avec données sensibles** :
- Méthodologie de référence MR-001 (recherche en santé)
- Désignation d'un DPO (Data Protection Officer)
- Étude d'impact (DPIA) si données à risque

### Health Data Hub (si applicable)

**Si données de santé individuelles** (actuellement non) :
- Certification Hébergeur de Données de Santé (HDS)
- Conformité aux référentiels de sécurité ASIP Santé
- Procédure d'autorisation CNIL/CNIL-CEREES

## Anonymisation et Agrégation

### Techniques Appliquées

#### 1. Agrégation Géographique
```python
# Exemple : comptage par département
departement_counts = df.groupby(['date', 'departement']).size()
# Pas de données individuelles conservées
```

**Niveau de protection** : k-anonymat (k ≥ 5 en général pour les urgences)

#### 2. Agrégation Temporelle
```python
# Moyennes sur fenêtres glissantes (7 jours)
rolling_avg = series.rolling(window=7).mean()
# Lissage supplémentaire des variations individuelles
```

#### 3. Suppression des Identifiants
- Pas de noms, prénoms, adresses
- Pas de numéros de sécurité sociale
- Pas de numéros de dossier patient

#### 4. Généralisation
- Départements/régions au lieu de villes
- Jours au lieu d'heures (pas de traçabilité fine)

### Risques Résiduels

**Risque de ré-identification** : **Très faible**
- Agrégation à plusieurs niveaux (département × jour)
- Pas de variables quasi-identifiantes
- Pas de croisement avec d'autres bases

**Risque de divulgation d'information** : **Faible**
- Statistiques de santé publique déjà publiques
- Pas d'information nouvelle sensible révélée

## Biais et Équité du Modèle

### Analyse des Biais Potentiels

#### 1. Biais Géographiques
**Risque** : Sur-représentation de certaines régions dans les données
**Mitigation** :
- Entraînement sur toutes les régions françaises
- Calcul de métriques par département (`predictions_summary.json`)
- Surveillance des erreurs par zone géographique

#### 2. Biais Temporels
**Risque** : Modèle performant sur certaines saisons mais pas d'autres
**Mitigation** :
- Données sur plusieurs années (captures des variations saisonnières)
- Features temporelles (mois, saison) si nécessaire
- Validation sur période de test représentative

#### 3. Biais de Mesure
**Risque** : Sous-déclaration dans certains départements
**Mitigation** :
- Documentation des sources de données
- Comparaison avec d'autres indicateurs (si disponibles)
- Prudence dans l'interprétation des prédictions

### Équité des Prédictions

**Objectif** : Performance équitable sur tous les départements

**Surveillance** :
```python
# Métriques par département
dept_metrics = predictions.groupby('departement').agg({
    'abs_error': 'mean',
    'rel_error': 'mean'
})
# Alertes si écart > 20% entre départements
```

**Actions correctives** :
- Rééquilibrage des données (si biais détecté)
- Modèles spécifiques par région (si nécessaire)
- Transparence sur les limites du modèle

## Utilisation Responsable

### Limites du Modèle

**À NE PAS FAIRE** :
- Utiliser pour décisions médicales individuelles
- Remplacer le jugement clinique
- Discriminer l'accès aux soins en fonction des prédictions
- Prendre des décisions RH basées sur les prédictions

**USAGE APPROPRIÉ** :
- Anticiper les besoins en personnel hospitalier
- Planifier les stocks de matériel médical
- Optimiser les capacités d'accueil
- Communication de prévention ciblée

### Communication des Résultats

**Transparence** :
- Marges d'erreur toujours communiquées (MAE, RMSE)
- Intervalles de confiance affichés
- Limites du modèle clairement expliquées

**Langage** :
- "Prédiction" ≠ "certitude"
- "Risque élevé" ≠ "garantie"
- "Estimation" basée sur données historiques

### Formation des Utilisateurs

**Avant déploiement** :
- Formation des équipes hospitalières à l'interprétation
- Sensibilisation aux biais potentiels
- Procédures de remontée d'anomalies

## Gouvernance des Données

### Rôles et Responsabilités

**Responsable du Projet** :
- Supervision générale
- Décisions sur les évolutions du modèle
- Interface avec les autorités (si requis)

**Data Scientists** :
- Développement et maintenance du pipeline
- Surveillance des performances
- Documentation des changements

**Utilisateurs Finaux** (hôpitaux, ARS) :
- Retours sur la qualité des prédictions
- Signalement des anomalies
- Respect des conditions d'utilisation

### Procédures de Mise à Jour

**Nouvelles données** :
1. Vérification de la conformité légale
2. Validation de la qualité
3. Documentation des changements
4. Tests de non-régression
5. Réentraînement du modèle

**Modification du modèle** :
1. Validation scientifique
2. Tests A/B si possible
3. Communication aux utilisateurs
4. Archivage de la version précédente

## Audit et Contrôle

### Audits Internes

**Fréquence** : Trimestrielle

**Éléments contrôlés** :
- Qualité des prédictions (métriques)
- Équité par département
- Conformité des processus
- Sécurité des accès

### Audits Externes

**Si déploiement en production** :
- Audit de sécurité par cabinet spécialisé
- Revue par comité d'éthique (si données sensibles)
- Certification ISO 27001 (gestion de la sécurité)

### Documentation des Incidents

**Procédure en cas de violation** :
1. Identification et confinement
2. Évaluation de l'impact
3. Notification aux autorités (si requis, sous 72h)
4. Communication aux personnes affectées (si applicable)
5. Mesures correctives

## Ressources et Contacts

### Références Légales

- **RGPD** : [Règlement (UE) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- **CNIL** : [Recherche en santé](https://www.cnil.fr/fr/recherche-medicale)
- **Licence Ouverte 2.0** : [Etalab](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)

### Contacts Utiles

- **CNIL** : 01 53 73 22 22 - [www.cnil.fr](https://www.cnil.fr)
- **Data.gouv.fr** : [support@data.gouv.fr](mailto:support@data.gouv.fr)
- **Health Data Hub** : [www.health-data-hub.fr](https://www.health-data-hub.fr)

### Documentation Complémentaire

- [Guide CNIL sur l'anonymisation](https://www.cnil.fr/sites/default/files/atoms/files/guide_anonymisation.pdf)
- [Référentiel ASIP Santé](https://esante.gouv.fr/)
- [Open Data Santé](https://www.data.gouv.fr/fr/pages/donnees-sante/)

## Engagement du Projet

**LUMEN s'engage à** :
- Traiter uniquement des données publiques et agrégées
- Respecter les principes éthiques de la recherche en santé
- Maintenir la transparence totale sur les méthodes
- Protéger rigoureusement les données contre tout usage abusif
- Améliorer continuellement les mesures de sécurité

**Dernière mise à jour** : 2025-10-27
