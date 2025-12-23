# Auteur Romain Lesueur

"""
Modele SQLAlchemy pour la table Region.

Represente une region geographique (ex: Western Europe, Northern America).
"""

from models import db


class Region(db.Model):
    """
    Classe ORM representant une region geographique.

    Attributes:
        id_region (int): Cle primaire auto-incrementee.
        nom_region (str): Nom de la region (unique).
        pays (list): Liste des pays appartenant a cette region.
    """

    __tablename__ = 'region'

    id_region = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_region = db.Column(db.Text, nullable=False, unique=True)

    # Relation 1-n vers Pays
    pays = db.relationship(
        'Pays',
        back_populates='region',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        """Representation textuelle de l'objet Region."""
        return f"<Region {self.id_region}: {self.nom_region}>"

    def to_dict(self):
        """
        Serialise l'objet Region en dictionnaire.

        Returns:
            dict: Dictionnaire contenant les attributs de la region.
        """
        return {
            'id_region': self.id_region,
            'nom_region': self.nom_region,
            'nb_pays': self.pays.count() if self.pays else 0
        }


