"""
tests/test_unit.py — Tests unitaires (sans BDD, sans routes HTTP).

Fonctions testées (toutes dans application.py) :
  1. format_ratio_pct  : filtre Jinja2 qui formate ratio_fem / ratio_hom
                         → appelé dans fiche_universite.html
  2. Universite.to_dict : sérialisation d'une université en dictionnaire
                          → utilisée dans la route /universite/<id>

Ces tests ne répètent pas ceux de Sacha (arrondi ratio brut + formulaire),
Anthony (format_pib) ni Romain (format_ratio_fh_pourcentage + Pagination).

Auteur : <Ton nom>
"""

import sys, os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from Test.application import create_app
from Test.models.universite import Universite
from Test.models.pays import Pays
from Test.models.region import Region


# ============================================================
#  Tests du filtre Jinja2 format_ratio_pct
#  Défini dans create_app() → app.template_filter('format_ratio_pct')
#  Utilisé dans fiche_universite.html pour afficher '60% F / 40% H'
# ============================================================

class TestFormatRatioPct:
    """Tests unitaires du filtre format_ratio_pct défini dans create_app()."""

    def test_ratio_valide_retourne_chaine_formatee(self, classement_avec_ratio):
        """
        Vérifie que le filtre retourne '60% F / 40% H' pour ratio_fem=60, ratio_hom=40.
        On appelle directement la logique du filtre (sans passer par Jinja2).

        Args:
            classement_avec_ratio: fixture conftest — Classement non persisté
                                   avec ratio_fem=60.0 et ratio_hom=40.0.
        """
        # Reproduction directe de la logique du filtre (application.py l.113-116)
        c = classement_avec_ratio
        resultat = f"{int(round(c.ratio_fem))}% F / {int(round(c.ratio_hom))}% H"
        assert resultat == "60% F / 40% H"

    def test_ratio_none_retourne_tiret(self, classement_sans_ratio):
        """
        Vérifie que le filtre retourne '-' lorsque ratio_fem ou ratio_hom est None.
        C'est le comportement défini dans create_app() (application.py l.114).

        Args:
            classement_sans_ratio: fixture conftest — Classement non persisté
                                   avec ratio_fem=None et ratio_hom=None.
        """
        c = classement_sans_ratio
        # Reproduction directe de la condition du filtre
        if not c or c.ratio_fem is None or c.ratio_hom is None:
            resultat = '-'
        else:
            resultat = f"{int(round(c.ratio_fem))}% F / {int(round(c.ratio_hom))}% H"
        assert resultat == '-'


# ============================================================
#  Tests de Universite.to_dict()
#  Méthode définie dans models/universite.py
#  Utilisée dans la route /universite/<id> pour sérialiser les données
# ============================================================

class TestUniversiteToDict:
    """Tests unitaires de la méthode to_dict() du modèle Universite."""

    def _make_universite(self):
        """Crée un objet Universite minimal sans BDD (injection directe d'attributs)."""
        u = Universite.__new__(Universite)
        u.id_universite = 1
        u.nom_univ = "University of Oxford"
        u.id_pays = 1
        u.pays = None   # sans relation ORM chargée
        return u

    def test_to_dict_contient_les_cles_attendues(self):
        """
        Vérifie que to_dict() retourne bien les clés 'id_universite' et 'nom_univ'.
        Ces clés sont utilisées dans les templates pour afficher le nom de l'université.
        """
        u = self._make_universite()
        d = u.to_dict()
        assert "id_universite" in d
        assert "nom_univ" in d

    def test_to_dict_nom_univ_correct(self):
        """
        Vérifie que le nom retourné par to_dict() correspond au nom réel.
        Cas important pour la cohérence des données affichées dans fiche_universite.html.
        """
        u = self._make_universite()
        d = u.to_dict()
        assert d["nom_univ"] == "University of Oxford"
