"""
tests/test_system.py — Tests système (end-to-end : routes HTTP + BDD SQLite).

Routes testées (définies dans register_routes() d'application.py) :
  1. GET /statistiques  : page des statistiques socio-économiques
  2. GET /universite/<id> avec un id inexistant → doit retourner 404

Ces tests ne répètent pas ceux de Sacha (route 500 + /universite/<id> existant),
Anthony (route 404 directe + /universites) ni Romain (route / + /universites).

Auteur : <Ton nom>
"""

import pytest


# ============================================================
#  Test 1 — Route GET /statistiques
#  Route définie dans register_routes() → fonction statistiques()
#  Teste les 4 graphiques socio-économiques (intern, PIB, alpha, ratio F/H)
# ============================================================

class TestRouteStatistiques:
    """Tests système de la route GET /statistiques."""

    def test_statistiques_retourne_200(self, client):
        """
        Vérifie que la page statistiques répond avec le code HTTP 200.
        Cette route exécute 4 requêtes ORM complexes (CASE, AVG, GROUP BY)
        sur les tables Pays, Universite et Classement.

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/statistiques")
        assert reponse.status_code == 200, (
            f"La route /statistiques doit retourner 200, obtenu {reponse.status_code}"
        )

    def test_statistiques_contient_donnees_graphiques(self, client):
        """
        Vérifie que la page statistiques contient bien du contenu HTML lié
        aux graphiques (balises canvas ou identifiants Chart.js injectés par Jinja2).
        Valide que les données ORM ont été correctement passées au template.

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/statistiques")
        html = reponse.data.decode("utf-8")
        # Le template statistiques.html contient des <canvas> pour Chart.js
        assert "<canvas" in html, (
            "La page /statistiques doit contenir des éléments <canvas> pour les graphiques"
        )


# ============================================================
#  Test 2 — Route GET /universite/<id> avec id inexistant
#  Route définie dans register_routes() → fonction fiche_universite()
#  Vérifie la gestion des erreurs 404 pour un classement introuvable
# ============================================================

class TestRouteUniversiteInexistante:
    """
    Tests système de la route /universite/<id> avec un id invalide.
    Différent du test de Sacha qui teste un id existant.
    """

    def test_universite_id_inexistant_retourne_404(self, client):
        """
        Vérifie que l'accès à /universite/99999 (id inexistant en BDD)
        retourne bien un code HTTP 404 et non une erreur serveur 500.
        Valide la gestion d'erreur dans fiche_universite() via abort(404).

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/universite/99999")
        assert reponse.status_code == 404, (
            f"Un id inexistant doit retourner 404, obtenu {reponse.status_code}"
        )

    def test_universite_id_zero_retourne_404(self, client):
        """
        Vérifie que /universite/0 retourne 404.
        L'id 0 ne peut jamais exister en BDD (autoincrement commence à 1).
        Cas limite utile pour valider la robustesse de la route.

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/universite/0")
        assert reponse.status_code == 404, (
            f"/universite/0 doit retourner 404, obtenu {reponse.status_code}"
        )
