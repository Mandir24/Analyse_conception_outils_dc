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

## 📌 Présentation du projet

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
│   ├── index.html          # Accueil : KPI + graphiques + Top 10
│   ├── universités.html    # Recherche filtrable + Top/Bottom 5
│   ├── fiche_universite.html # Fiche détaillée + storytelling
│   ├── statistiques.html   # Graphiques socio-économiques
│   ├── 404.html
│   └── 500.html
│
├── static/                 # CSS et JS
├── data/                   # Fichiers CSV source
│
└── tests/                  # ← Suite de tests (SAÉ S6)
    ├── conftest.py
    ├── test_unit.py
    ├── test_integration.py
    └── test_system.py
```

---

## ⚙️ Stack technique

<div align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,sqlite,html,css,js,github,vscode&theme=dark"/>
</div>

| Couche | Technologie |
|---|---|
| Backend | Flask 3, Flask-SQLAlchemy, Flask-WTF |
| Base de données | SQLite (production) · SQLite `:memory:` (tests) |
| Visualisation | Chart.js |
| Templates | Jinja2 + Bootstrap |
| Data processing | Pandas, NumPy |
| Tests | pytest, pytest-cov |

---

##  Lancer l'application

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
# → http://localhost:5000
```

---

##  Dépendances

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

> Tests réalisés individuellement : **Mandir Diop**.  

### Structure

```
tests/
├── conftest.py          # Toutes les fixtures (BDD SQLite en mémoire + données CSV échantillon)
├── test_unit.py         # Tests unitaires — sans BDD
├── test_integration.py  # Tests d'intégration — BDD SQLite, sans routes
└── test_system.py       # Tests système — end-to-end via client HTTP
```

---

###  Unitaires (`test_unit.py`) — sans BDD

Fonctions testées directement, sans aucune base de données ni route HTTP.

| # | Fonction testée | Fichier source | Ce qui est vérifié |
|---|---|---|---|
| 1 | Filtre Jinja2 `format_ratio_pct` | `application.py` | `ratio_fem=60, ratio_hom=40` → `"60% F / 40% H"` |
| 2 | Filtre Jinja2 `format_ratio_pct` | `application.py` | `ratio_fem=None` → retourne `"-"` sans erreur |
| 3 | `Universite.to_dict()` | `models/universite.py` | Le dictionnaire contient les clés `id_universite` et `nom_univ` |
| 4 | `Universite.to_dict()` | `models/universite.py` | La valeur `nom_univ` est bien celle de l'objet |

```bash
pytest tests/test_unit.py -v
```

---

###  Intégration (`test_integration.py`) — BDD SQLite en mémoire, sans routes

Requêtes ORM testées directement sur la BDD, sans passer par HTTP.

| # | Comportement testé | Route source dans `application.py` | Ce qui est vérifié |
|---|---|---|---|
| 1 | Requête top pays par `indic_enseig` (ORDER BY DESC) | `index()` → graphique `data_top_pays_enseig` | UK (Oxford 92.1) devance USA (MIT 91.2) |
| 2 | Tri décroissant des scores top pays | `index()` → graphique `data_top_pays_enseig` | La liste est bien triée de haut en bas |
| 3 | Relation ORM `Universite.classements.all()` | `fiche_universite()` → graphique d'évolution | Oxford a 2 classements en BDD (2023 + 2024) |
| 4 | Ordre chronologique des classements | `fiche_universite()` → storytelling | Les classements sont triés par année croissante |

```bash
pytest tests/test_integration.py -v
```

---

###  Système (`test_system.py`) — end-to-end via client HTTP

Routes testées de bout en bout : requête HTTP → ORM → rendu Jinja2 → réponse HTML.

| # | Route | Ce qui est vérifié |
|---|---|---|
| 1 | `GET /statistiques` | Code HTTP 200 |
| 2 | `GET /statistiques` | Présence de `<canvas>` dans le HTML (graphiques Chart.js injectés) |
| 3 | `GET /universite/99999` | Code HTTP 404 (id inexistant en BDD) |
| 4 | `GET /universite/0` | Code HTTP 404 (id impossible, autoincrement commence à 1) |

```bash
pytest tests/test_system.py -v
```

---

###  Lancer tous les tests + couverture

```bash
# Tous les tests
pytest tests/ -v

# Avec rapport de couverture HTML (à déposer sur Ecampus)
pytest tests/ --cov=. --cov-report=html -v
# → dossier htmlcov/ généré
```

---

### 🗄️ BDD de test

Tous les tests utilisent une **BDD SQLite en mémoire** (`sqlite:///:memory:`) peuplée par `_seed_db()` dans `conftest.py`. Aucun fichier CSV ni BDD de production n'est utilisé.

Échantillon inséré :

| Table | Données |
|---|---|
| `Region` | Western Europe, Northern America |
| `Pays` | United Kingdom (PIB 46 510 $), United States (PIB 63 000 $) |
| `Universite` | University of Oxford, MIT |
| `Classement` | Oxford 2023, Oxford 2024, MIT 2024 |

---

## 📊 Pages de l'application

| Page | URL | Contenu |
|---|---|---|
| Accueil | `/` | 9 KPI · Top 5 pays enseignement/recherche · Pie chart régions · Top 10 |
| Universités | `/universites` | Top/Bottom 5 · Formulaire de recherche filtrable |
| Fiche université | `/universite/<id>` | Indicateurs complets · Graphique d'évolution · Storytelling |
| Statistiques | `/statistiques` | 4 graphiques socio-économiques (PIB, alphabétisation, ratio F/H, internationalisation) |

---

<div align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=tokyonight" alt="Quote"/>
</div>

<p align="center">
  <i>Fait avec ❤️ par <b>Mandir Diop</b> · BUT VCOD · IUT Grand Ouest Normandie</i>
</p>
