<div align="center">
  <img src="https://visitor-badge.laobi.icu/badge?page_id=Mandir24.Analyse_conception_outils_dc&color=7aa2f7" alt="visiteurs"/>
</div>

<h1 align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&pause=1000&color=7aa2f7&center=true&vCenter=true&width=700&lines=🎓+World-Univ-Rank;Analyse+mondiale+des+universités;Flask+%7C+SQLite+%7C+Chart.js" alt="Typing SVG" />
  </a>
</h1>

<p align="center">
  <b>SAÉ 5 & 6 · BUT Sciences des Données (VCOD) · IUT Grand Ouest Normandie</b><br/>
  <i>Application web d'analyse et de visualisation du classement mondial THE des universités (2016–2025)</i>
</p>

<div align="center">
  <a href="https://www.linkedin.com/in/mandir-diop-92bab6276/" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Mandir_Diop-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a>
  <a href="mailto:diopmandir53@gmail.com">
    <img src="https://img.shields.io/badge/Email-diopmandir53@gmail.com-7aa2f7?style=for-the-badge&logo=gmail&logoColor=white"/>
  </a>
  <a href="https://www.mandir-diop.com" target="_blank">
    <img src="https://img.shields.io/badge/Portfolio-mandir--diop.com-bb9af7?style=for-the-badge&logo=googlechrome&logoColor=black"/>
  </a>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-in--memory-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/pytest-passing-2ECC71?style=flat-square&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/coverage-html-F39C12?style=flat-square"/>
</div>

---

## Présentation du projet

**World-Univ-Rank** est une application web Flask qui analyse les données du classement **Times Higher Education (THE)** sur la période **2016–2025**, enrichies d'indicateurs socio-économiques par pays (PIB, alphabétisation, migration, etc.).

L'objectif : comprendre ce qui distingue les systèmes universitaires d'excellence à l'échelle mondiale.

---

##  Structure du projet

```
Analyse_conception_outils_dc/
│
├── application.py          # Point d'entrée Flask + routes + filtres Jinja2
├── config.py               # Configurations (dev, prod, testing)
├── launch_project.py       # Script de lancement
│
├── models/
│   ├── __init__.py
│   ├── region.py           # Modèle Region
│   ├── pays.py             # Modèle Pays
│   ├── universite.py       # Modèle Universite
│   └── classement.py       # Modèle Classement
│
├── scripts/
│   ├── clean_data.py       # Nettoyage et fusion des CSV (Pandas / NumPy)
│   └── populate_db.py      # Peuplement de la BDD via ORM SQLAlchemy
│
├── templates/              # Pages HTML (Jinja2 + Bootstrap)
│   ├── base.html
│   ├── index.html
│   ├── universités.html
│   ├── fiche_universite.html
│   ├── statistiques.html
│   ├── 404.html
│   └── 500.html
│
├── static/                 # CSS et JS
├── data/                   # Fichiers CSV source
│
└── tests/ Test de de l'application (SAE : Développement et test d'un outil décisionnel)
    ├── conftest.py
    ├── test_unit.py
    ├── test_integration.py
    └── test_system.py
```

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Flask 3, Flask-SQLAlchemy, Flask-WTF |
| Base de données | SQLite (production) · SQLite `:memory:` (tests) |
| Visualisation | Chart.js |
| Templates | Jinja2 + Bootstrap |
| Data processing | Pandas, NumPy |
| Tests | pytest, pytest-cov |

---

## Lancer l'application

```bash
# 1. Cloner le dépôt
git clone https://github.com/Mandir24/Analyse_conception_outils_dc.git
cd Analyse_conception_outils_dc

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Peupler la base de données
python scripts/populate_db.py

# 4. Lancer l'application
python application.py
# -> http://localhost:5000
```

---

## Dépendances

| Paquet | Version | Usage |
|---|---|---|
| `Flask` | 3.1.3 | Framework web |
| `Flask-SQLAlchemy` | 3.1.1 | ORM SQLite |
| `Flask-WTF` | 1.2.2 | Formulaires de recherche |
| `WTForms` | 3.2.1 | Validation des champs |
| `pandas` | 3.0.1 | Nettoyage des CSV |
| `numpy` | 2.4.3 | Traitement numérique |
| `gunicorn` | latest | Déploiement production |
| `pytest` | 9.0.3 | Suite de tests |
| `pytest-cov` | 7.1.0 | Rapport de couverture |

```bash
pip install -r requirements.txt
```

---

##  Tests — SAÉ S6

> Tests réalisés individuellement par **Mandir Diop**.
> Distincts des tests de Sacha, Anthony et Romain (aucune répétition).

### Structure

```
tests/
├── conftest.py          # Fixtures : BDD SQLite en mémoire + données échantillon
├── test_unit.py         # 2 tests unitaires — sans BDD, sans routes
├── test_integration.py  # 2 tests d'intégration — BDD SQLite, sans routes
└── test_system.py       # 2 tests système — end-to-end via client HTTP
```

---

###  Unitaires (`test_unit.py`) — sans BDD

Logique du filtre Jinja2 `format_pib` testée directement, sans base de données ni route HTTP.

| # | Fonction testée | Fichier source | Ce qui est vérifié |
|---|---|---|---|
| 1 | Filtre `format_pib` | `application.py` | `46510.0` -> `"46 510 $"` (séparateur milliers + symbole $) |
| 2 | Filtre `format_pib` | `application.py` | `1000000` -> `"1 000 000 $"` (plusieurs séparateurs de milliers) |

```bash
pytest tests/test_unit.py -v
```

**Pourquoi ces 2 cas ?**
Le cas 1 valide le comportement nominal avec un PIB réaliste (UK en données de test).
Le cas 2 valide que la fonction gère correctement plusieurs groupes de milliers — un remplacement naïf de virgule par espace pourrait rater ce cas sur des nombres à 7+ chiffres.

---

###  Intégration (`test_integration.py`) — BDD SQLite en mémoire, sans routes

Requêtes ORM testées directement sur la BDD, sans passer par HTTP.

| # | Comportement testé | Source dans `application.py` | Ce qui est vérifié |
|---|---|---|---|
| 1 | Requête top pays par `indic_enseig` (JOIN + AVG + ORDER BY DESC) | `index()` -> graphique `data_top_pays_enseig` | UK (Oxford 92.1) devance USA (MIT 91.2) |
| 2 | Relation ORM `Universite.classements.all()` triée par année | `fiche_universite()` -> graphique d'évolution | Oxford a 2 classements, retournés de 2023 -> 2024 |

```bash
pytest tests/test_integration.py -v
```

**Pourquoi ces 2 cas ?**
Le test 1 valide une requête complexe (JOIN sur 3 tables + GROUP BY + ORDER BY) qui est au cœur du graphique page d'accueil. Si le ORDER BY saute, le graphique s'affiche dans le mauvais sens.
Le test 2 valide la configuration de la relation ORM : si `order_by` est absent du modèle Universite, les classements arrivent dans un ordre aléatoire et le graphique d'évolution devient incohérent.

---

###  Système (`test_system.py`) — end-to-end via client HTTP

Routes testées de bout en bout : requête HTTP -> ORM -> rendu Jinja2 -> réponse HTML.

| # | Route | Ce qui est vérifié |
|---|---|---|
| 1 | `GET /statistiques` | Code HTTP 200 (les 4 requêtes ORM complexes s'exécutent sans erreur) |
| 2 | `GET /statistiques` | Présence de `"United Kingdom"` dans le HTML (les données ORM arrivent bien jusqu'au template) |

```bash
pytest tests/test_system.py -v
```

**Pourquoi ces 2 cas ?**
Le test 1 (code 200) valide que la route ne plante pas. Mais un 200 seul peut masquer une page vide si les données ne sont pas passées au template. Le test 2 complète en vérifiant qu'un nom de pays réel — inséré par `_seed_db()` — apparaît bien dans le HTML rendu, validant ainsi toute la chaîne ORM -> Jinja2.

---

###  Lancer tous les tests + couverture

```bash
# Tous les tests
pytest tests/ -v

# Avec rapport de couverture HTML
pytest tests/ --cov=. --cov-report=html -v
# -> dossier htmlcov/ généré
```

---

###  BDD de test

Tous les tests utilisent une **BDD SQLite en mémoire** (`sqlite:///:memory:`) peuplée par `_seed_db()` dans `conftest.py`. Aucun fichier CSV ni BDD de production n'est utilisé.

| Table | Données |
|---|---|
| `Region` | Western Europe, Northern America |
| `Pays` | United Kingdom (PIB 46 510 $), United States (PIB 63 000 $) |
| `Universite` | University of Oxford, MIT |
| `Classement` | Oxford 2023, Oxford 2024, MIT 2024 |

---

##  Pages de l'application

| Page | URL | Contenu |
|---|---|---|
| Accueil | `/` | 9 KPI · Top 5 pays enseignement/recherche · Pie chart régions · Top 10 |
| Universités | `/universites` | Top/Bottom 5 · Formulaire de recherche filtrable |
| Fiche université | `/universite/<id>` | Indicateurs complets · Graphique d'évolution · Storytelling |
| Statistiques | `/statistiques` | 4 graphiques socio-économiques (PIB, alphabétisation, ratio F/H, internationalisation) |

---


