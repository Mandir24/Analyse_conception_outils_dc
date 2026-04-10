"""
conftest.py — Fixtures partagées pour les tests (unit, integration, system).

Toutes les fixtures sont centralisées ici conformément aux consignes SAÉ S6.
Ces tests sont distincts de ceux réalisés par Sacha, Anthony et Romain.

Auteur : Mandir Diop
"""

import pytest
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from application import create_app
from models import db as _db
from models.region import Region
from models.pays import Pays
from models.universite import Universite
from models.classement import Classement


# ============================================================
#  FIXTURES UNITAIRES  (sans BDD)
# ============================================================

@pytest.fixture
def ratio_fem_hom_valide():
    """
    Dictionnaire simulant les champs ratio_fem et ratio_hom d'un Classement.
    Utilisé pour tester la logique du filtre format_ratio_pct sans SQLAlchemy.
    Le filtre est défini dans create_app() → application.py et appelé dans
    le template fiche_universite.html.
    """
    return {"ratio_fem": 60.0, "ratio_hom": 40.0}


@pytest.fixture
def ratio_fem_hom_none():
    """
    Dictionnaire simulant les champs ratio_fem=None et ratio_hom=None.
    Permet de tester le cas où les données sont absentes du CSV.
    Le filtre format_ratio_pct doit retourner '-' dans ce cas.
    """
    return {"ratio_fem": None, "ratio_hom": None}


# ============================================================
#  FIXTURES D'INTÉGRATION  (BDD SQLite en mémoire, sans routes)
# ============================================================

@pytest.fixture(scope="function")
def app_test():
    """
    Instance Flask configurée en mode testing avec BDD SQLite en mémoire.
    Légère et isolée entre chaque test.
    """
    app = create_app("testing")
    app.config.update({
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "cle-test-sae",
    })
    with app.app_context():
        _db.create_all()
        _seed_db()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def db_session(app_test):
    """
    Session SQLAlchemy active pour les tests d'intégration.
    """
    with app_test.app_context():
        yield _db.session


# ============================================================
#  FIXTURES SYSTÈME  (client HTTP end-to-end)
# ============================================================

@pytest.fixture(scope="function")
def client(app_test):
    """
    Client HTTP Flask pour les tests système.
    """
    return app_test.test_client()


# ============================================================
#  HELPER PRIVÉ : peuplement de la BDD de test
# ============================================================

def _seed_db():
    """
    Insère un échantillon minimal représentatif du CSV dans la BDD SQLite mémoire.
    """
    europe = Region(nom_region="Western Europe")
    amerique = Region(nom_region="Northern America")
    _db.session.add_all([europe, amerique])
    _db.session.flush()

    uk = Pays(nom_pays="United Kingdom", population=67_000_000,
              pib_hab=46_510.0, alphabetisation_pct=99.0,
              tel_1000hab=1185.0, id_region=europe.id_region)
    usa = Pays(nom_pays="United States", population=331_000_000,
               pib_hab=63_000.0, alphabetisation_pct=99.0,
               tel_1000hab=1300.0, id_region=amerique.id_region)
    _db.session.add_all([uk, usa])
    _db.session.flush()

    oxford = Universite(nom_univ="University of Oxford", id_pays=uk.id_pays)
    mit = Universite(nom_univ="Massachusetts Institute of Technology", id_pays=usa.id_pays)
    _db.session.add_all([oxford, mit])
    _db.session.flush()

    classements = [
        Classement(annee=2024, rang=1, pop_etud=24000, ratio_etud_pers=11.4,
                   etud_internationaux_pct=42.0, ratio_fem_hom="52:48",
                   score_global=96.4, indic_enseig=92.1, indic_env_rech=99.7,
                   indic_qualite_rech=97.3, indic_impact_industrie=74.0,
                   indic_rel_intern=96.2, ratio_fem=52.0, ratio_hom=48.0,
                   id_univ=oxford.id_universite),
        Classement(annee=2023, rang=2, pop_etud=23500, ratio_etud_pers=11.2,
                   etud_internationaux_pct=41.0, ratio_fem_hom="51:49",
                   score_global=95.0, indic_enseig=91.0, indic_env_rech=98.5,
                   indic_qualite_rech=96.0, indic_impact_industrie=72.0,
                   indic_rel_intern=95.0, ratio_fem=51.0, ratio_hom=49.0,
                   id_univ=oxford.id_universite),
        Classement(annee=2024, rang=2, pop_etud=11520, ratio_etud_pers=8.0,
                   etud_internationaux_pct=33.0, ratio_fem_hom="43:57",
                   score_global=94.5, indic_enseig=91.2, indic_env_rech=98.1,
                   indic_qualite_rech=96.3, indic_impact_industrie=88.0,
                   indic_rel_intern=82.5, ratio_fem=43.0, ratio_hom=57.0,
                   id_univ=mit.id_universite),
    ]
    _db.session.add_all(classements)
    _db.session.commit()
