# Auteur Sacha Ucendo

"""
Modele SQLAlchemy pour la table Pays.

Represente une Pays (ex: France, Allemagne).
"""


from models import db


class Pays(db.Model):
    """
    Classe ORM representant un pays.

    Attributes:
        id_pays (int): Cle primaire auto-incrementee.
        nom_pays (str): Nom du pays (unique).
        population (int): Population totale.
        superf_m2 (float): Superficie en m2.
        pib_hab (float): PIB par habitant.
        migration_nette (float): Solde migratoire.
        industrie_part (float): Part de l'industrie dans le PIB.
        services_part (float): Part des services dans le PIB.
        alphabetisation_pct (float): Taux d'alphabetisation (%).
        tel_1000hab (float): Telephones pour 1000 habitants.
        id_region (int): Cle etrangere vers Region.
        region (Region): Relation vers la region.
        universites (list): Liste des universites du pays.
    """

    __tablename__ = 'pays'

    id_pays = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_pays = db.Column(db.Text, nullable=False, unique=True)
    population = db.Column(db.Integer, nullable=True)
    superf_m2 = db.Column(db.Float, nullable=True)
    pib_hab = db.Column(db.Float, nullable=True)
    migration_nette = db.Column(db.Float, nullable=True)
    industrie_part = db.Column(db.Float, nullable=True)
    services_part = db.Column(db.Float, nullable=True)
    alphabetisation_pct = db.Column(db.Float, nullable=True)
    tel_1000hab = db.Column(db.Float, nullable=True)
    id_region = db.Column(
        db.Integer,
        db.ForeignKey('region.id_region', ondelete='SET NULL'),
        nullable=True
    )

    # Relations
    region = db.relationship('Region', back_populates='pays', lazy='select')
    universites = db.relationship(
        'Universite',
        back_populates='pays',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        """Representation textuelle de l'objet Pays."""
        return f"<pays {self.id_pays}: {self.nom_pays}>"
    
    def to_dict(self):
        """
        Serialise l'objet Pays en dictionnaire.

        Returns:
            dict: Dictionnaire contenant les attributs du pays.
        """
        return {
            'id_pays' : self.id_pays ,
            'nom_pays' : self.nom_pays,
            'population' : self.population,
            'superf_m2' : self.superf_m2,
            'pib_hab' : self.pib_hab,
            'migration_nette' : self.migration_nette,
            'industrie_part' : self.industrie_part,
            'services_part' : self.services_part,
            'alphabetisation_pct' : self.alphabetisation_pct,
            'tel_1000hab' : self.tel_1000hab,
            'id_region' : self.id_region
        }