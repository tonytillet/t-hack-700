# 📊 Sources de données

## Sources officielles

### Sentinelles -  SentiWeb

- **URL** : [https://www.sentiweb.fr/france/fr/?page=table](https://www.sentiweb.fr/france/fr/?page=table)
- **Données** : 
    - Syndromes grippaux - National - hebdomadaire - Sentinelle;IQVIA;EMR
    - Syndromes grippaux - Région - hebdomadaire - Sentinelle;IQVIA;EMR
- **Description** : Données des syndromes grippaux collectées par les médecins sentinelles depuis 1985 à aujourd'hui.
- **Fréquence** : Hebdomadaire
- **Format** : JSON

### Santé Publique France
- **Urgences** : Passages aux urgences pour syndrome grippal
- **Sentinelles** : Réseau de médecins sentinelles
- **Vaccination** : Taux de vaccination par région
- **IAS** : Indicateurs d'activité syndromique

**URL :** [https://www.santepubliquefrance.fr/](https://www.santepubliquefrance.fr/)

### INSEE
- **Population** : Données démographiques par région
- **Démographie** : Structure par âge de la population
- **Densité** : Concentration de population

**URL :** [https://www.insee.fr/](https://www.insee.fr/)

### Météo France
- **Température** : Données de température moyenne
- **Humidité** : Taux d'humidité
- **Conditions météo** : Facteurs climatiques favorisant la grippe

**URL :** [https://meteofrance.com/](https://meteofrance.com/)

## Sources complémentaires

### Google Trends
- **Recherches** : Tendances de recherche pour termes liés à la grippe
- **Évolution** : Changements temporels des recherches

**URL :** [https://trends.google.com/](https://trends.google.com/)

### Wikipedia
- **Pages vues** : Consultation des pages sur la grippe
- **Intérêt public** : Mesure de l'attention portée au sujet

**URL :** [https://www.mediawiki.org/wiki/API:Main_page](https://www.mediawiki.org/wiki/API:Main_page)

## Fréquence de mise à jour

- **Données de santé** : Hebdomadaire
- **Données météo** : Quotidienne
- **Tendances de recherche** : Quotidienne
- **Données démographiques** : Annuelle

## Format des données

Toutes les données sont collectées et converties au format CSV pour un traitement uniforme.

### Structure type

```csv
date,region,urgences_grippe,vaccination_2024,ias_syndrome_grippal,population_totale,pct_65_plus,temperature,humidite
2024-10-21,Île-de-France,125,67.5,2.3,12000000,18.5,12.3,75.2
```
