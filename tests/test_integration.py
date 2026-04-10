"""
tests/test_integration.py — Tests d'intégration (BDD SQLite en mémoire, sans routes HTTP).

Comportements testés (issus de application.py) :
  1. Requête ORM top pays par score d'enseignement (indic_enseig)
     → utilisée dans index() pour le graphique data_top_pays_enseig
  2. Relation ORM Universite → Classement (.classements.all())
     → utilisée dans fiche_universite() pour construire l'historique annuel

Ces tests ne répètent pas ceux de Sacha (insertion Région/Classement),
Anthony (insertion Université, filtre classement par année),
ni Romain (insertion Pays, to_dict, filtre université par pays).

Auteur : Mandir Diop
"""

import pytest
from models import db
from models.classement import Classement
from models.pays import Pays
from models.universite import Universite


# ============================================================
#  Test 1 — Requête top pays par score d'enseignement
#  Correspond à la requête top_pays_enseig dans index() d'application.py
#  → Graphique en barres "Top pays enseignement" sur la page d'accueil
# ============================================================

class TestTopPaysEnseignement:
    """
    Teste la requête ORM qui calcule le classement des pays par score
    d'enseignement moyen (indic_enseig).

    Cette requête fait appel à :
        - JOIN Pays → Universite → Classement
        - GROUP BY Pays.nom_pays
        - AVG(Classement.indic_enseig)
        - ORDER BY DESC
        - FILTER annee == 2024

    Elle est directement issue de la route index() dans application.py
    et alimente le graphique Chart.js data_top_pays_enseig.
    """

    def test_premier_pays_est_celui_avec_meilleur_score(self, app_test):
        """
        Vérifie que le pays en première position est celui dont
        la moyenne indic_enseig est la plus élevée pour l'année 2024.

        Données fixture (_seed_db) :
            UK   → Oxford  2024 : indic_enseig = 92.1
            USA  → MIT     2024 : indic_enseig = 91.2
        Résultat attendu : UK en tête.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            resultats = (
                db.session.query(
                    Pays.nom_pays,
                    db.func.avg(Classement.indic_enseig).label("score"),
                )
                .select_from(Pays)
                .join(Universite, Pays.id_pays == Universite.id_pays)
                .join(Classement, Universite.id_universite == Classement.id_univ)
                .filter(Classement.annee == 2024)
                .group_by(Pays.nom_pays)
                .order_by(db.desc("score"))
                .limit(5)
                .all()
            )

            assert len(resultats) >= 1, "La requête doit retourner au moins un résultat"
            premier_pays = resultats[0][0]
            assert premier_pays == "United Kingdom", (
                f"UK devrait être en tête (Oxford 92.1 > MIT 91.2), "
                f"obtenu : {premier_pays}"
            )

    def test_scores_sont_tries_par_ordre_decroissant(self, app_test):
        """
        Vérifie que les scores retournés sont triés du plus élevé au plus bas.

        Propriété essentielle pour que le graphique Chart.js affiche
        correctement les barres du plus performant au moins performant.
        Un tri incorrect rendrait le graphique trompeur pour l'utilisateur.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            resultats = (
                db.session.query(
                    Pays.nom_pays,
                    db.func.avg(Classement.indic_enseig).label("score"),
                )
                .select_from(Pays)
                .join(Universite, Pays.id_pays == Universite.id_pays)
                .join(Classement, Universite.id_universite == Classement.id_univ)
                .filter(Classement.annee == 2024)
                .group_by(Pays.nom_pays)
                .order_by(db.desc("score"))
                .limit(5)
                .all()
            )

            scores = [float(r[1]) for r in resultats]
            assert scores == sorted(scores, reverse=True), (
                f"Les scores doivent être triés en ordre décroissant, "
                f"obtenu : {scores}"
            )


# ============================================================
#  Test 2 — Relation ORM Universite.classements
#  Utilisée dans fiche_universite() pour construire l'historique
#  annuel et le graphique d'évolution des scores
# ============================================================

class TestRelationUniversiteClassements:
    """
    Teste la relation ORM Universite → Classement via .classements.all().

    Cette relation est définie dans models/universite.py et exploitée
    dans fiche_universite() pour construire :
        - le graphique d'évolution des scores (Chart.js ligne)
        - le bloc storytelling de la fiche

    On vérifie deux propriétés indépendantes :
        1. Le nombre de classements associés à une université
        2. L'ordre chronologique de retour (order_by='annee' dans le modèle)
    """

    def test_universite_a_le_bon_nombre_de_classements(self, app_test):
        """
        Vérifie qu'Oxford possède exactement 2 classements (2023 et 2024)
        via la relation ORM .classements.all().

        Ce compte est critique : c'est lui qui détermine le nombre de points
        sur le graphique d'évolution dans fiche_universite.html.
        Un classement manquant = un point absent sur la courbe.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            oxford = Universite.query.filter_by(
                nom_univ="University of Oxford"
            ).first()
            assert oxford is not None, "Oxford doit exister en BDD"

            historique = oxford.classements.all()
            assert len(historique) == 2, (
                f"Oxford doit avoir 2 classements (2023 + 2024), "
                f"obtenu : {len(historique)}"
            )

    def test_classements_retournes_par_annee_croissante(self, app_test):
        """
        Vérifie que les classements d'Oxford sont retournés dans l'ordre
        chronologique croissant (2023 avant 2024).

        L'ordre est défini par order_by='annee' dans le modèle Universite.
        Il est indispensable pour que l'axe X du graphique Chart.js
        représente une chronologie cohérente de gauche à droite.

        Args:
            app_test: fixture conftest — app Flask + BDD SQLite peuplée.
        """
        with app_test.app_context():
            oxford = Universite.query.filter_by(
                nom_univ="University of Oxford"
            ).first()
            historique = oxford.classements.all()
            annees = [c.annee for c in historique]
            assert annees == sorted(annees), (
                f"Les classements doivent être triés par année croissante, "
                f"obtenu : {annees}"
            )
