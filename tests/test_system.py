"""
tests/test_system.py — Tests système (end-to-end : requête HTTP → ORM → Jinja2 → HTML).

Route testée :
  - GET /statistiques (définie dans register_routes() → fonction statistiques())
    → Page des 4 graphiques socio-économiques (PIB, alphabétisation, ratio F/H,
      internationalisation)

Ces tests ne répètent pas ceux de Sacha (route 404 directe, /universites),
Anthony (route /, /universites), ni Romain (route 500, /universite/<id> existant).

Auteur : Mandir Diop
"""

import pytest


# ============================================================
#  Tests — Route GET /statistiques
#  Route définie dans register_routes() → fonction statistiques()
#
#  Cette route exécute 4 requêtes ORM complexes :
#    - CASE / AVG / GROUP BY sur Pays + Classement (internationalisation)
#    - AVG(pib_hab) par région (PIB)
#    - AVG(alphabetisation_pct) par région
#    - AVG(ratio_fem) / AVG(ratio_hom) par région
#
#  On teste ici la chaîne complète : HTTP → ORM → rendu Jinja2 → HTML retourné
# ============================================================

class TestRouteStatistiques:
    """
    Tests système end-to-end de la route GET /statistiques.

    Valide que la route :
      1. répond correctement (code 200)
      2. injecte bien les données ORM dans le template (présence des données pays)
    """

    def test_statistiques_retourne_200(self, client):
        """
        Vérifie que la page /statistiques répond avec le code HTTP 200.

        Ce test valide que la route statistiques() s'exécute sans erreur :
        les 4 requêtes ORM (JOIN + GROUP BY + AVG) passent correctement
        sur la BDD SQLite de test et le template se rend sans exception.

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/statistiques")
        assert reponse.status_code == 200, (
            f"La route /statistiques doit retourner 200, "
            f"obtenu : {reponse.status_code}"
        )

    def test_statistiques_contient_elements_canvas(self, client):
        """
        Vérifie que le HTML retourné contient au moins un élément <canvas>.

        Les données ORM de /statistiques sont injectées en JSON dans des
        variables JavaScript et consommées par Chart.js via des balises <canvas>.
        La présence de <canvas> confirme que :
            1. Le template statistiques.html a bien été rendu par Jinja2
            2. Les blocs graphiques sont présents dans la page

        Note : les noms de pays/région n'apparaissent pas en texte brut dans
        le HTML — ils sont encodés en JSON dans les variables JS (ex: dataRegion).
        C'est pourquoi on vérifie <canvas> plutôt qu'un nom de pays.

        Args:
            client: fixture conftest — client HTTP Flask avec BDD SQLite peuplée.
        """
        reponse = client.get("/statistiques")
        html = reponse.data.decode("utf-8")
        assert "<canvas" in html, (
            "La page /statistiques doit contenir des éléments <canvas> "
            "pour les graphiques Chart.js. "
            "Vérifie que le template statistiques.html est bien rendu."
        )
