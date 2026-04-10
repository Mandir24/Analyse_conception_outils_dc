"""
tests/test_unit.py — Tests unitaires (sans BDD, sans routes HTTP).

Fonctions testées (toutes dans application.py) :
  1. Logique du filtre Jinja2 format_ratio_pct
     → défini dans create_app(), appelé dans fiche_universite.html
  2. Logique du filtre Jinja2 format_pib
     → défini dans create_app(), appelé dans fiche_universite.html

Ces tests ne répètent pas ceux de Sacha, Anthony et Romain.
On teste la logique pure sans instancier d'objets SQLAlchemy.

Auteur : Mandir Diop
"""

import sys
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


# ============================================================
#  Helpers : reproduction directe des logiques des filtres
#  définis dans create_app() → application.py
# ============================================================

def _format_ratio_pct(ratio_fem, ratio_hom):
    """
    Reproduction de la logique du filtre format_ratio_pct (application.py l.113-116).
    Retourne 'X% F / Y% H' ou '-' si les valeurs sont None.
    """
    if ratio_fem is None or ratio_hom is None:
        return '-'
    return f"{int(round(ratio_fem))}% F / {int(round(ratio_hom))}% H"


def _format_pib(value):
    """
    Reproduction de la logique du filtre format_pib (application.py l.119-121).
    Retourne un PIB formaté avec espaces et symbole $ ou '-' si None.
    """
    if value is None:
        return "-"
    return f"{int(value):,}".replace(",", " ") + " $"


# ============================================================
#  Tests du filtre format_ratio_pct
#  Défini dans create_app() → application.py
#  Utilisé dans fiche_universite.html pour afficher '60% F / 40% H'
# ============================================================

class TestFormatRatioPct:
    """Tests unitaires de la logique du filtre format_ratio_pct."""

    def test_ratio_valide_retourne_chaine_formatee(self, ratio_fem_hom_valide):
        """
        Vérifie que ratio_fem=60, ratio_hom=40 retourne '60% F / 40% H'.

        Args:
            ratio_fem_hom_valide: fixture conftest → {"ratio_fem": 60.0, "ratio_hom": 40.0}
        """
        resultat = _format_ratio_pct(
            ratio_fem_hom_valide["ratio_fem"],
            ratio_fem_hom_valide["ratio_hom"]
        )
        assert resultat == "60% F / 40% H"

    def test_ratio_none_retourne_tiret(self, ratio_fem_hom_none):
        """
        Vérifie que ratio_fem=None retourne '-' sans erreur.
        Correspond aux données manquantes dans le CSV THE.

        Args:
            ratio_fem_hom_none: fixture conftest → {"ratio_fem": None, "ratio_hom": None}
        """
        resultat = _format_ratio_pct(
            ratio_fem_hom_none["ratio_fem"],
            ratio_fem_hom_none["ratio_hom"]
        )
        assert resultat == '-'


# ============================================================
#  Tests du filtre format_pib
#  Défini dans create_app() → application.py
#  Utilisé dans fiche_universite.html pour afficher le PIB/habitant
# ============================================================

class TestFormatPib:
    """Tests unitaires de la logique du filtre format_pib."""

    def test_pib_valide_retourne_chaine_formatee(self):
        """
        Vérifie que 46510.0 retourne '46 510 $'.
        Le format avec espaces comme séparateur de milliers est défini
        dans le filtre format_pib de application.py.
        """
        resultat = _format_pib(46510.0)
        assert resultat == "46 510 $"

    def test_pib_none_retourne_tiret(self):
        """
        Vérifie que None retourne '-' sans erreur.
        Cas fréquent pour les pays sans données PIB dans le CSV.
        """
        resultat = _format_pib(None)
        assert resultat == "-"
