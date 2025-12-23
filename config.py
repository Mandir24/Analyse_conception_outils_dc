import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Classe de configuration de base
    SQLALCHEMY_ECHO : afficher les requêtes dans le terminal
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'univ.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    DATA_DIR = os.path.join(BASE_DIR,"data")
    CSV_THE = os.path.join(DATA_DIR, "Classement_THE_des_universites_mondiales_2016–2025.csv")
    CSV_FUSIONNE = os.path.join(DATA_DIR, "donnees_fusionnees.csv")
    CSV_PAYS = os.path.join(DATA_DIR, "statistiques_pays_du_monde.csv")

class DevelopmentConfig(Config):
    """
    Classe de configuration pour le developpement
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuration pour la production."""

    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()


class TestingConfig(Config):
    """Configuration pour les tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionnaire de configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
