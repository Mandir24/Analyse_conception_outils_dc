# World-Univ-Rank - Guide de lancement

Application web d'analyse mondiale de la performance universitaire basée sur les classements THE (Times Higher Education) 2016-2025.

---

## Prérequis

- **Python 3.8+** installé sur votre machine
- **pip** (gestionnaire de paquets Python)

---

## Installation initiale

```bash
# Cloner le repository
git clone https://github.com/Mandir24/Analyse_conception_outils_dc.git
cd analyse-et-conception-outil-decisionnel

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# Installer les dépendances
pip install -r requirement.txt
```

---

## Méthode 1 : Lancement manuel (étape par étape)

Cette méthode vous permet de contrôler chaque étape du processus.

### Étape 1 : Nettoyer et fusionner les données

```bash
python scripts/clean_data.py
```

**Ce que fait ce script :**
- Charge les fichiers CSV bruts depuis le dossier `data/`
- Nettoie les données (valeurs manquantes, formats)
- Fusionne les données de classement avec les statistiques des pays
- Génère le fichier `data/donnees_fusionnees.csv`

### Étape 2 : Peupler la base de données

```bash
python scripts/populate_db.py
```

**Ce que fait ce script :**
- Lit le fichier `data/donnees_fusionnees.csv`
- Crée la base de données SQLite `univ.db`
- Crée les tables (Region, Pays, Universite, Classement)
- Insère toutes les données dans la base

### Étape 3 : Lancer l'application

```bash
python application.py
```

**Ce que fait ce script :**
- Démarre le serveur Flask
- L'application sera accessible sur : **http://localhost:5000**

### Résumé de la méthode 1

```bash
# Commandes à exécuter une par une :
python scripts/clean_data.py
python scripts/populate_db.py
python application.py
```

---

## Méthode 2 : Lancement automatique (une seule commande)

utilisez le script de lancement automatique qui exécute toutes les étapes à la suite.

### Commande unique

```bash
python launch_project.py
```

**Ce que fait ce script :**
1. Nettoie et fusionne les données CSV
2. Crée et peuple la base de données SQLite
3. Lance automatiquement l'application Flask
4. Affiche les logs de chaque étape

### Résumé de la méthode 2

```bash
# Une seule commande pour tout lancer :
python launch_project.py
```

---

## Pages disponibles

| Route | Description |
|-------|-------------|
| `/` | Page d'accueil avec KPI et graphiques généraux |
| `/universites` | Liste des universités avec filtres et graphiques comparatifs |
| `/universite/<id>` | Fiche détaillée d'une université |
| `/statistiques` | Analyses statistiques et corrélations socio-économiques |
| `/test-500` | Page d'erreur 500 |

---

##  Technologies utilisées

- **Backend** : Flask, SQLAlchemy, Flask-WTF
- **Frontend** : Bootstrap 5, Chart.js, Jinja2
- **Data** : Pandas, NumPy
- **Database** : SQLite




