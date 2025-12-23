# Auteur Sacha Ucendo

"""
Modele SQLAlchemy pour la table Classement.

Represente le classement des universités (ex: 1er : université A, 2ème : université B).
"""


from models import db


class Classement(db.Model):
    """
    Classe ORM representant le classement des universités.

    Attributes:
    id_classement (int): Cle primaire auto-incrementee.
    annee (int): Année.
    rang (int): Rang de l'université.
    pop_etud (int): Nombre d'étudiant.
    ratio_etud_pers (float): Ratio d'étudiant par rapport au nombre d'habitant.
    etud_internationaux_pct (float): Indice de la part d’étudiants venant de l’étranger.
    ratio_fem_hom (float): Le rapport « femmes / hommes » parmi les étudiants.
    score_global (float): Le score global attribué à l’université selon la méthode THE.
    indic_enseig (float): Sous-indicateur relatif à l’enseignement / environnement d’apprentissage.
    indic_env_rech (float): Score ou sous-indicateur relatif à l’environnement de recherche.
    indic_qualite_rech (float): Score ou sous-indicateur relatif à la qualité de la recherche.
    indic_impact_industrie (float): Score ou sous-indicateur relatif à l’impact industriel / transfert / collaboration industrie-université.
    indic_rel_intern (float): Score ou sous-indicateur relatif à l’ouverture internationale / collaboration internationale / mixité.
    ratio_fem (float): Le rapport « femmes / population » parmi les étudiants.
    ratio_hom (float): Le rapport « hommes / population » parmi les étudiants.
    id_univ (int): identifiant de l'université (clé étrangère vers université)
    """

    __tablename__ = 'classement'
    id_classement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    annee = db.Column(db.Integer)
    rang = db.Column(db.Integer)
    pop_etud = db.Column(db.Integer)
    ratio_etud_pers = db.Column(db.Float)
    etud_internationaux_pct = db.Column(db.Float)
    ratio_fem_hom = db.Column(db.Text, nullable=True)
    score_global = db.Column(db.Float)
    indic_enseig = db.Column(db.Float)
    indic_env_rech = db.Column(db.Float)
    indic_qualite_rech = db.Column(db.Float)
    indic_impact_industrie = db.Column(db.Float)
    indic_rel_intern = db.Column(db.Float)
    ratio_fem = db.Column(db.Float)
    ratio_hom = db.Column(db.Float)
    id_univ = db.Column(
        db.Integer,
        db.ForeignKey('universite.id_universite', ondelete='CASCADE'),
        nullable=False
    )
    # Relation N-1 avec Université
    universite = db.relationship(
        'Universite',
        back_populates='classements',
        lazy='select'
    )
    
    def __repr__(self):
        """Representation textuelle de l'objet Classement."""
        return f"<Classement {self.id_classement}: {self.rang}>"
    
    def to_dict(self):
        """
        Serialise l'objet Classement en dictionnaire.

        Returns:
            dict: Dictionnaire contenant les attributs du pays.
        """
        return {
            'id_classement' : self.id_classement,
            'annee' : self.annee,
            'rang' : self.rang,
            'pop_etud' : self.pop_etud,
            'ratio_etud_pers' : self.ratio_etud_pers,
            'etud_internationaux_pct' : self.etud_internationaux_pct,
            'ratio_fem_hom' : self.ratio_fem_hom,
            'score_global' : self.score_global,
            'indic_enseig' : self.indic_enseig,
            'indic_env_rech' : self.indic_env_rech,
            'indic_qualite_rech' : self.indic_qualite_rech,
            'indic_impact_industrie' : self.indic_impact_industrie,
            'indic_rel_intern' : self.indic_rel_intern,
            'ratio_fem' : self.ratio_fem,
            'ratio_hom' : self.ratio_hom,
            'id_univ' : self.id_univ
        }