# Auteur Romain Lesueur

"""
Modeles SQLAlchemy pour le projet World-Univ-Rank.

Ce module initialise Flask-SQLAlchemy et expose les modeles ORM :
- Region : Regions geographiques
- Pays : Pays avec statistiques socio-economiques
- Universite : Universites (entite stable)
- Classement : Classements annuels THE (donnees variables)
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.region import Region
from models.pays import Pays
from models.universite import Universite
from models.classement import Classement

__all__ = ['db', 'Region', 'Pays', 'Universite', 'Classement']
