"""
tests/test_integration.py — Tests d'intégration (BDD SQLite en mémoire, sans routes HTTP).

Fonctions/comportements testés (issus de application.py) :
  1. Requête top 5 pays par score d'enseignement
     → utilisée dans index() pour le graphique data_top_pays_enseig
  2. Relation ORM Universite → Classement (accès via .classements.all())
     → utilisée dans la route /universite/<id> pour construire l'historique

Ces tests ne répètent pas ceux de Sacha (insertion Pays), Anthony (insertion Région/Classement)
ni Romain (insertion Université + filtre classement par année).

Auteur : <Ton nom>
"""

import pytest
from models import db
from models.classement import Classement
from models.pays import Pays
from models.universite import Universite


# ============================================================
#  Test 1 — Requête Top 5 pays par score d'enseignement
#  Correspond à la requête top_pays_enseig dans index() d'application.py
# ============================================================

class TestTopPaysEnseignement:
    """
    Teste la requête ORM qui calcule le top pays par score d'enseignement.
    Cette requête est utilisée dans la route index() pour construire
    data_top_pays_enseig (graphique en barres page d'accueil).
    """

    def test_premier_pays_est_celui_avec_meilleur_score(self, app_test):
        """
        Vérifie que le pays retourné en première position est celui dont
        la moyenne indic_enseig est la plus élevée pour l'année 2024.
        Données fixture : UK (Oxford=92.1) vs USA (MIT=91.2) → UK en tête.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            resultats = db.session.query(
                Pays.nom_pays,
                db.func.avg(Classement.indic_enseig).label('score')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == 2024
            ).group_by(Pays.nom_pays).order_by(db.desc('score')).limit(5).all()

            assert len(resultats) >= 1
            premier_pays = resultats[0][0]
            assert premier_pays == "United Kingdom", (
                f"UK devrait être en tête avec Oxford (92.1) > MIT (91.2), "
                f"obtenu : {premier_pays}"
            )

    def test_scores_sont_tries_par_ordre_decroissant(self, app_test):
        """
        Vérifie que les scores retournés sont bien triés du plus haut au plus bas.
        Propriété essentielle pour que le graphique Chart.js s'affiche correctement.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            resultats = db.session.query(
                Pays.nom_pays,
                db.func.avg(Classement.indic_enseig).label('score')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == 2024
            ).group_by(Pays.nom_pays).order_by(db.desc('score')).limit(5).all()

            scores = [float(r[1]) for r in resultats]
            assert scores == sorted(scores, reverse=True), (
                "Les scores doivent être triés en ordre décroissant"
            )


# ============================================================
#  Test 2 — Relation ORM Universite.classements
#  Utilisée dans la route /universite/<id> pour récupérer l'historique
#  annuel et construire le storytelling + graphique d'évolution
# ============================================================

class TestRelationUniversiteClassements:
    """
    Teste la relation ORM Universite → Classement (.classements.all()).
    Cette relation est exploitée dans la route fiche_universite() pour
    construire l'historique d'évolution des scores (graphique en ligne).
    """

    def test_universite_a_plusieurs_classements(self, app_test):
        """
        Vérifie qu'Oxford possède bien 2 classements (2023 et 2024) via la relation ORM.
        C'est ce résultat qui alimente le graphique d'évolution dans fiche_universite.html.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            oxford = Universite.query.filter_by(nom_univ="University of Oxford").first()
            assert oxford is not None
            historique = oxford.classements.all()
            assert len(historique) == 2, (
                f"Oxford doit avoir 2 classements (2023 et 2024), obtenu {len(historique)}"
            )

    def test_classements_tries_par_annee_croissante(self, app_test):
        """
        Vérifie que les classements d'Oxford sont retournés par année croissante
        (order_by='Classement.annee' défini dans models/universite.py).
        L'ordre est crucial pour que le graphique Chart.js affiche l'évolution
        chronologique correctement.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            oxford = Universite.query.filter_by(nom_univ="University of Oxford").first()
            historique = oxford.classements.all()
            annees = [c.annee for c in historique]
            assert annees == sorted(annees), (
                f"Les classements doivent être triés par année croissante, obtenu {annees}"
            )
