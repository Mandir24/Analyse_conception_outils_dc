import os
import sys
import logging
import pandas as pd
from pathlib import Path

# Ajout du repertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from application import create_app
from models import db, Region, Pays, Universite, Classement
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def charger_csv(chemin):
    """
    Fonction :

        Lit un fichier CSV et retourne un DataFrame pandas

    Params :

        chemin : str
        Le chemin complet vers le fichier CSV à charger

    Return :

        type : pandas.DataFrame ou None
        Le DataFrame chargé si le fichier est valide, sinon None
    """
    try:
        # Tentative de lecture du fichier CSV
        df = pd.read_csv(chemin)
        logger.info(f"Fichier chargé : {chemin} ({len(df)} lignes)" )
        return df
    except FileNotFoundError:
        # Cas où le fichier n'existe pas à l'emplacement donné
        logger.error(f"Fichier introuvable {chemin}")
        return None
    except Exception as e :
        # Toutes les autres erreurs 
        logger.error(f"Erreur lors du chargement : {chemin} : {e}")
        return None


# Auteur : Anthony YON

def peupler_regions(df):

    """
    Fonction :

        Ajoute dans la base toutes les régions présentes dans le fichier de données fusionnées 
        et retourne un dictionnaire (exemple :{nom_region: objet Region})

    Params :
    
        df : pandas.DataFrame
        Le DataFrame contenant une colonne 'region'

    Return :
    
        type : dict
        Un mapping où chaque clé est un nom de région, et chaque valeur est l'objet Region correspondant
    """

    # On extrait toutes les valeurs distinctes présentes dans la colonne "region"
    # Objectif : connaître la liste des régions à insérer dans la base
    regions_uniques = df['region'].dropna().unique()

    # Création du mapping : il servira à stocker pour chaque nom de région l'objet Region créé
    mapping = {}

    for nom in regions_uniques:
        # Vérification si une région avec ce nom existe déjà dans la base
        region = Region.query.filter_by(nom_region = nom).first()
        
        if not region:
            # On crée une nouvelle instance de Region avec le nom trouvé dans le csv
            region = Region(nom_region = nom) 
            # on ajoute l'instance à la session 
            db.session.add(region)
            # Message pour connaître la région ajoutée
            logger.debug(f"Région ajoutée : {nom}")
        mapping[nom] = region

    # Validation de toutes les insertions et updates faites dans la session
    db.session.commit()
    # Log informatif
    logger.info(f"Régions existantes : {len(mapping)}")
    return mapping



# Auteur : Anthony YON

def peupler_pays(df,region_mapping):

    """
    Fonction :

        Ajoute dans la base tous les pays présents dans le fichier de données fusionnées
        et retourne un dictionnaire (exemple : {nom_pays: objet Pays})

    Params :

        df : pandas.DataFrame
            Le DataFrame contenant une colonne 'pays'
        
        region_mapping : dict
            Un dictionnaire de type {nom_region: objet Region} retourné par la
            fonction peupler_regions() (Il permet d’associer chaque pays à sa région)

    Return :

        type : dict
        Un mapping où chaque clé est un nom de pays, et chaque valeur est l'objet Pays correspondant 
    """

    # Une seule ligne par pays (garde la première occurrence)
    pays_uniques = df.groupby('pays').first().reset_index()
    
    # Création du mapping : il servira à stocker pour chaque nom de région l'objet Pays créé
    mapping = {}

    for _, row in pays_uniques.iterrows():
        nom = row['pays']
        # Vérifie si le pays existe déjà 
        pays = Pays.query.filter_by(nom_pays=nom).first()

        if not pays:
            # Nom de la région dans la ligne CSV
            nom_region = row.get('region')
            # Objet Region correspondant (grâce au mapping retourné par peupler_regions())
            region_obj = region_mapping.get(nom_region) if nom_region else None

            # Création de l'objet Pays avec conversion des valeurs
            # utilisation du .get() pour éviter les KeyError (retourne None si clé inconnue)
            pays = Pays(
                    nom_pays=nom,
                    population = int(row.get('population')) if pd.notna(row.get('population')) else None,
                    superf_m2 = float(row.get('superf_m2')) if pd.notna(row.get('superf_m2')) else None,
                    pib_hab = float(row.get('pib_hab')) if pd.notna(row.get('pib_hab')) else None,
                    migration_nette = float(row.get('migration_nette')) if pd.notna(row.get('migration_nette')) else None,
                    industrie_part = float(row.get('industrie_part')) if pd.notna(row.get('industrie_part')) else None,
                    services_part = float(row.get('services_part')) if pd.notna(row.get('services_part')) else None,
                    alphabetisation_pct = float(row.get('alphabetisation_pct')) if pd.notna(row.get('alphabetisation_pct')) else None,
                    tel_1000hab = float(row.get('tel_1000hab')) if pd.notna(row.get('tel_1000hab')) else None,
                    id_region=region_obj.id_region if region_obj else None
                ) 

            # Ajout à la session SQLAlchemy
            db.session.add(pays)
            logger.debug(f"Pays ajouté : {nom}")

        # Ajoute au mapping 
        mapping[nom] = pays

    # Sauvegarde en base
    db.session.commit()
    logger.info(f"Pays existants : {len(mapping)}")
    return mapping


def peupler_universites(df, pays_mapping):
    """
    Insere les universites uniques dans la base.

    Args:
        df (pd.DataFrame): DataFrame avec colonnes nom_univ et pays.
        pays_mapping (dict): Mapping nom_pays -> objet Pays.

    Returns:
        dict: Mapping (nom_univ, pays) -> objet Universite.
    """
    # Universites uniques
    univ_uniques = df[['nom_univ', 'pays']].drop_duplicates()
    mapping = {}

    for _, row in univ_uniques.iterrows():
        nom = row['nom_univ']
        pays_nom = row['pays']

        # Cle composite pour gerer les homonymes dans differents pays
        cle = (nom, pays_nom)

        univ = Universite.query.filter_by(nom_univ=nom).first()
        if not univ:
            pays = pays_mapping.get(pays_nom)
            univ = Universite(
                nom_univ=nom,
                id_pays=pays.id_pays if pays else None
            )
            db.session.add(univ)
            logger.debug(f"Universite ajoutee: {nom}")

        mapping[cle] = univ

    db.session.commit()
    logger.info(f"{len(mapping)} universites inserees/existantes")
    return mapping


def peupler_classements(df, univ_mapping):
    """
    Insere les classements annuels dans la base.

    Args:
        df (pd.DataFrame): DataFrame complet avec tous les classements.
        univ_mapping (dict): Mapping (nom_univ, pays) -> objet Universite.

    Returns:
        int: Nombre de classements inseres.
    """
    count = 0

    for _, row in df.iterrows():
        cle = (row['nom_univ'], row['pays'])
        univ = univ_mapping.get(cle)

        if not univ:
            logger.warning(f"Universite non trouvee: {cle}")
            continue

        # Verifier si le classement existe deja
        annee = int(row['annee'])
        existe = Classement.query.filter_by(
            id_univ=univ.id_universite,
            annee=annee
        ).first()

        if existe:
            logger.debug(f"Classement existant: {univ.nom_univ} - {annee}")
            continue

        classement = Classement(
            annee=annee,
            rang=float(row['rang']) if pd.notna(row.get('rang')) else None,
            pop_etud=float(row['pop_etud']) if pd.notna(row.get('pop_etud')) else None,
            ratio_etud_pers=float(row['ratio_etud_pers']) if pd.notna(row.get('ratio_etud_pers')) else None,
            etud_internationaux_pct=float(row['etud_internationaux_pct']) if pd.notna(row.get('etud_internationaux_pct')) else None,
            ratio_fem_hom=str(row['ratio_fem_hom']) if pd.notna(row.get('ratio_fem_hom')) else None,
            ratio_fem=float(row['ratio_fem']) if pd.notna(row.get('ratio_fem')) else None,
            ratio_hom=float(row['ratio_hom']) if pd.notna(row.get('ratio_hom')) else None,
            score_global=float(row['score_global']) if pd.notna(row.get('score_global')) else None,
            indic_enseig=float(row['indic_enseig']) if pd.notna(row.get('indic_enseig')) else None,
            indic_env_rech=float(row['indic_env_rech']) if pd.notna(row.get('indic_env_rech')) else None,
            indic_qualite_rech=float(row['indic_qualite_rech']) if pd.notna(row.get('indic_qualite_rech')) else None,
            indic_impact_industrie=float(row['indic_impact_industrie']) if pd.notna(row.get('indic_impact_industrie')) else None,
            indic_rel_intern=float(row['indic_rel_intern']) if pd.notna(row.get('indic_rel_intern')) else None,
            id_univ=univ.id_universite
        )
        db.session.add(classement)
        count += 1

        # Commit par batch de 1000
        if count % 1000 == 0:
            db.session.commit()
            logger.info(f"{count} classements inseres...")

    db.session.commit()
    logger.info(f"{count} classements inseres au total")
    return count

def main():
    """
    Fonction principale de peuplement.
    Auteur : Romain Lesueur
    """
    logger.info("=" * 60)
    logger.info("DEBUT DU PEUPLEMENT DE LA BASE DE DONNEES")
    logger.info("=" * 60)

    # Creation de l'application Flask
    app = create_app('development')

    with app.app_context():
        # Suppression des tables existantes (optionnel)
        logger.info("Reinitialisation des tables...")
        db.drop_all()
        db.create_all()

        # Chargement du CSV fusionne
        csv_path = Config.CSV_FUSIONNE
        df = charger_csv(csv_path)

        if df is None:
            logger.error("Impossible de charger les donnees. Arret.")
            sys.exit(1)

        # Peuplement des tables
        logger.info("-" * 40)
        logger.info("Insertion des regions...")
        regions_mapping = peupler_regions(df)

        logger.info("-" * 40)
        logger.info("Insertion des pays...")
        pays_mapping = peupler_pays(df, regions_mapping)

        logger.info("-" * 40)
        logger.info("Insertion des universites...")
        univ_mapping = peupler_universites(df, pays_mapping)

        logger.info("-" * 40)
        logger.info("Insertion des classements...")
        peupler_classements(df, univ_mapping)

        # Resume final
        logger.info("=" * 60)
        logger.info("RESUME DU PEUPLEMENT")
        logger.info("=" * 60)
        logger.info(f"Regions:      {Region.query.count()}")
        logger.info(f"Pays:         {Pays.query.count()}")
        logger.info(f"Universites:  {Universite.query.count()}")
        logger.info(f"Classements:  {Classement.query.count()}")
        logger.info("=" * 60)
        logger.info("PEUPLEMENT TERMINE AVEC SUCCES")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()

