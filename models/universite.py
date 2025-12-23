# Auteur Sacha Ucendo

"""
Modele SQLAlchemy pour la table Universite.

Represente une Université (ex: California Institute of Technology, Yale University).
"""


from models import db


class Universite(db.Model):
    """
    Classe ORM representant une université .

    Attributes:
    id_universite (int): Cle primaire auto-incrementee.
    nom_univ (str): Nom de l'université.
    id_pays (int): Identifiant du pays (clé étrangère vers Pays).
    """

    __tablename__ = 'universite'
    id_universite = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_univ = db.Column(db.Text)
    id_pays = db.Column(db.Integer,
        db.ForeignKey('pays.id_pays',ondelete="SET NULL"))
    
    # Relation N-1 avec Pays
    
    # Relation 1-n vers Classement
    pays = db.relationship('Pays', back_populates='universites', lazy='select')
    classements = db.relationship(
        'Classement',
        back_populates='universite',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='Classement.annee'
    )
    
    def __repr__(self):
        """Representation textuelle de l'objet Universite."""
        return f"<Universite {self.id_universite}: {self.nom_univ}>"
    
    def to_dict(self, include_classements=False):
        """
        Serialise l'objet Universite en dictionnaire.

        Args:
            include_classements (bool): Inclure les classements annuels.

        Returns:
            dict: Dictionnaire contenant les attributs de l'universite.
        """
        data = {
            'id_universite': self.id_universite,
            'nom_univ': self.nom_univ,
            'pays': self.pays.nom_pays if self.pays else None,
            'region': self.pays.region.nom_region if self.pays and self.pays.region else None
        }

        if include_classements:
            data['classements'] = [c.to_dict() for c in self.classements.all()]

        return data