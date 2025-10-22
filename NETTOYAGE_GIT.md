# Nettoyage Git - Résolution du problème de taille des fichiers

## Problème initial
- Impossible de faire `git push` à cause de fichiers trop volumineux
- Le dépôt contenait des fichiers de données et des modèles ML très lourds

## Étapes de résolution

### 1. Identification du problème
- Vérification du statut Git avec `git status`
- Découverte que le dossier `data/` était encore tracké malgré le `.gitignore`

### 2. Suppression du dossier data/ du tracking Git
- Le dossier `data/` contenait des fichiers de plusieurs centaines de MB :
  - `data/raw/data.gouv.fr_20251021_205955_resource.json` : **772 MB**
  - `data/frozen/` : fichiers de 772 MB, 148 MB, 73 MB, etc.
  - `data/processed/predictions.csv` : **159 MB**
  - `data/cleaned/` : fichiers de 150 MB, 148 MB, 75 MB, etc.

**Action effectuée :**
- Le dossier `data/` était déjà dans `.gitignore` (lignes 102 et 109)
- Confirmation qu'il n'était plus tracké par Git avec `git ls-files data/`

### 3. Identification des fichiers volumineux trackés
**Commande utilisée :**
```bash
git ls-files | xargs ls -lh | sort -k5 -hr | head -10
```

**Résultat :**
- `ml/artefacts/enhanced_rf_model_20251021_234501.joblib` : **254 MB** ⚠️
- `ml/artefacts/random_forest.pkl` : **177 KB**

### 4. Exclusion des modèles ML volumineux
**Modification du `.gitignore` :**
```gitignore
# Modèles générés (ne pas committer)
models/*.pkl
models/*.joblib
models/*.json
models/*.csv
ml/artefacts/*.joblib  # ← AJOUTÉ
ml/artefacts/*.pkl     # ← AJOUTÉ
```

**Suppression du tracking Git :**
```bash
git rm --cached ml/artefacts/enhanced_rf_model_20251021_234501.joblib
git rm --cached ml/artefacts/random_forest.pkl
```

### 5. Commit des changements
```bash
git add .gitignore
git commit -m "Nettoyage: suppression du dossier data/ du tracking Git"
git commit -m "Exclusion des modèles ML volumineux du tracking Git"
```

## Résultat final

### Fichiers exclus du tracking Git :
- ✅ **Dossier `data/`** (plusieurs GB de données)
- ✅ **Modèles ML volumineux** (254 MB + 177 KB)
- ✅ **Fichiers de données temporaires**

### Fichiers conservés localement :
- Tous les fichiers restent disponibles sur la machine locale
- Seuls les fichiers de code et de configuration sont versionnés
- Les données et modèles sont ignorés par Git mais présents localement

### Configuration `.gitignore` mise à jour :
```gitignore
# Données générées
data/**
!data/.gitkeep
!data/**/.gitkeep

# Modèles générés (ne pas committer)
models/*.pkl
models/*.joblib
models/*.json
models/*.csv
ml/artefacts/*.joblib
ml/artefacts/*.pkl

# Autres exclusions...
```

## Avantages de cette approche :
1. **Réduction drastique de la taille** du dépôt Git
2. **Conservation des données** localement pour le développement
3. **Exclusion automatique** des futurs fichiers volumineux
4. **Possibilité de push** sans problème de taille
5. **Séparation claire** entre code versionné et données locales

## Recommandations pour l'avenir :
- Utiliser Git LFS pour les gros fichiers si nécessaire
- Maintenir une documentation des sources de données
- Créer des scripts de téléchargement des données si partage nécessaire
- Garder les modèles entraînés dans un stockage séparé (cloud, NAS, etc.)
