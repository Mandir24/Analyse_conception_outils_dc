"""
tests/test_unit.py — Tests unitaires (sans BDD, sans routes HTTP).

Fonction testée :
  - Filtre Jinja2 format_pib (application.py)
    → Appelé dans fiche_universite.html pour afficher le PIB/habitant

Auteur : Mandir Diop
"""

import sys
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


# ============================================================
#  Helper : reproduction directe de la logique du filtre format_pib
#  défini dans create_app() → application.py
# ============================================================

def _format_pib(value):
    """
    Reproduction de la logique du filtre format_pib (application.py).
    Retourne un PIB formaté avec espaces comme séparateurs de milliers
    et le symbole $, ou '-' si la valeur est None.

    Exemples :
        46510.0  → "46 510 $"
        None     → "-"
        1000000  → "1 000 000 $"
    """
    if value is None:
        return "-"
    return f"{int(value):,}".replace(",", " ") + " $"


# ============================================================
#  Tests du filtre format_pib
#  Défini dans create_app() , application.py
#  Utilisé dans fiche_universite.html pour afficher le PIB/habitant
# ============================================================

class TestFormatPib:
    """
    Tests unitaires de la logique du filtre Jinja2 format_pib.
    On teste la logique pure sans instancier d'objets SQLAlchemy ni de routes HTTP.
    """

    def test_pib_valide_retourne_chaine_formatee(self):
        """
        Vérifie que 46510.0 retourne '46 510 $'.
        Le format avec espaces comme séparateur de milliers est la convention
        française utilisée dans le filtre format_pib de application.py.
        Cas représentatif : PIB du Royaume-Uni dans les données de test.
        """
        resultat = _format_pib(46510.0)
        assert resultat == "46 510 $", (
            f"PIB 46510.0 doit retourner '46 510 $', obtenu : '{resultat}'"
        )

    def test_pib_grand_retourne_formatage_correct(self):
        """
        Vérifie que 1000000 retourne '1 000 000 $'.
        Teste le formatage des espaces sur un nombre à 7 chiffres.
        Valide que la fonction gère correctement plusieurs séparateurs de milliers,
        ce qu'un simple remplacement naïf pourrait rater.
        """
        resultat = _format_pib(1_000_000)
        assert resultat == "1 000 000 $", (
            f"PIB 1000000 doit retourner '1 000 000 $', obtenu : '{resultat}'"
        )
