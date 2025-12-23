import pandas as pd
import sys
import logging
from pathlib import Path

# --- Configuration des chemins et des logs ---
# Ajout du chemin parent pour les imports (assure la résolution des modules locaux)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importations des modules locaux
from application import create_app
from models import Region, Pays, Universite, Classement, db
from config import Config 

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# --- Fonctions de base ---

# Auteur : Mandir / Romain Lesueur (initialisation/structure)
def lire_csv(chemin):
    """
    Fonction : Lit un fichier CSV et retourne un DataFrame pandas.
    """
    try:
        df = pd.read_csv(chemin, encoding='utf-8') 
        logger.info(f"Fichier chargé : {chemin} ({len(df)} lignes)" )
        return df
    except FileNotFoundError:
        logger.error(f"Fichier introuvable {chemin}")
        return None
    except Exception as e :
        logger.error(f"Erreur lors du chargement : {chemin} : {e}")
        return None


# --- Fonctions de peuplement des tables de dimension ---

# Auteur : Anthony YON
def peupler_regions(df):
    """
    Peuple la table Region et retourne un mapping nom -> objet Region.
    """
    regions_uniques = df['region'].dropna().unique()
    mapping = {}

    for nom in regions_uniques:
        region = db.session.query(Region).filter_by(nom_region=nom).first()
        
        if not region:
            region = Region(nom_region=nom) 
            db.session.add(region)
            logger.debug(f"Région ajoutée : {nom}")
        
        mapping[nom] = region

    db.session.commit()
    logger.info(f"Régions existantes : {len(mapping)}")
    return mapping


# Auteur : Anthony YON
def peupler_pays(df, region_mapping):
    """
    Peuple la table Pays et retourne un mapping nom -> objet Pays.
    """
    pays_uniques = df.groupby('pays', dropna=True).first().reset_index()
    
    mapping = {}

    for _, row in pays_uniques.iterrows():
        nom = row['pays']
        pays = db.session.query(Pays).filter_by(nom_pays=nom).first()

        if not pays:
            nom_region = row.get('region')
            region_obj = region_mapping.get(nom_region) if nom_region else None

            data = {
                'nom_pays': nom,
                'population': int(row.get('population')) if pd.notna(row.get('population')) else None, 
                'superf_m2': float(row.get('superf_m2')) if pd.notna(row.get('superf_m2')) else None,
                'pib_hab': float(row.get('pib_hab')) if pd.notna(row.get('pib_hab')) else None,
                'migration_nette': float(row.get('migration_nette')) if pd.notna(row.get('migration_nette')) else None,
                'industrie_part': float(row.get('industrie_part')) if pd.notna(row.get('industrie_part')) else None,
                'services_part': float(row.get('services_part')) if pd.notna(row.get('services_part')) else None,
                'alphabetisation_pct': float(row.get('alphabetisation_pct')) if pd.notna(row.get('alphabetisation_pct')) else None,
                'tel_1000hab': float(row.get('tel_1000hab')) if pd.notna(row.get('tel_1000hab')) else None,
                'id_region': region_obj.id_region if region_obj else None
            }
            pays = Pays(**data) 

            db.session.add(pays)
            logger.debug(f"Pays ajouté : {nom}")

        mapping[nom] = pays

    db.session.commit()
    logger.info(f"Pays existants : {len(mapping)}")
    return mapping


# Auteur : Mandir
def peupler_universites(df, region_mapping):
    """
    Peuple la table Universite, lie les universités aux régions, 
    et retourne un mapping nom -> objet Universite.
    """
    universites_data = df[['nom_univ', 'region']].drop_duplicates().dropna(subset=['nom_univ', 'region'])
    mapping = {}

    for index, row in universites_data.iterrows():
        nom_univ = row['nom_univ']
        nom_region = row['region']
        
        region_obj = region_mapping.get(nom_region)
        
        if not region_obj:
            logger.warning(f"Région non trouvée pour l'université {nom_univ} : {nom_region}. Sautée.")
            continue

        universite = db.session.query(Universite).filter_by(nom_univ=nom_univ).first()
        
        if not universite:          
            universite = Universite(nom_univ=nom_univ, id_region=region_obj.id_region) 
            db.session.add(universite)
            logger.debug(f"Université ajoutée : {nom_univ} (Région: {nom_region})")
        
        mapping[nom_univ] = universite
        
    db.session.commit()
    logger.info(f"Nombre d'Universités traitées : {len(mapping)}")
    return mapping


# Auteur : Mandir
def peupler_classement(df, universite_mapping):
    """Peuple la table Classement (table de faits)."""

    count = 0
    
    for index, row in df.iterrows():
        nom_univ = row.get('nom_univ')
        
        if pd.isna(nom_univ) or nom_univ not in universite_mapping:
            logger.debug(f"Université '{nom_univ}' non trouvée/valide dans le mapping. Ligne {index} ignorée.")
            continue

        universite_obj = universite_mapping[nom_univ]
        annee = row.get('annee')
        
        if pd.notna(annee):
            existing_classement = db.session.query(Classement).filter_by(
                id_univ=universite_obj.id_univ,
                annee=int(annee) 
            ).first()

            if existing_classement:
                logger.debug(f"Classement pour {nom_univ} ({annee}) existe déjà. Ignoré.")
                continue

        try:
            classement_data = {
                'id_univ': universite_obj.id_univ, 
                'annee': int(row.get('annee')) if pd.notna(row.get('annee')) else None,
                'rang': int(row.get('rang')) if pd.notna(row.get('rang')) else None,
                'pop_etud': int(row.get('pop_etud')) if pd.notna(row.get('pop_etud')) else None,
                'ratio_etud_pers': float(row.get('ratio_etud_pers')) if pd.notna(row.get('ratio_etud_pers')) else None,
                'etud_internationaux_pct': float(row.get('etud_internationaux_pct')) if pd.notna(row.get('etud_internationaux_pct')) else None,
                'ratio_fem_hom': float(row.get('ratio_fem_hom')) if pd.notna(row.get('ratio_fem_hom')) else None,
                'score_global': float(row.get('score_global')) if pd.notna(row.get('score_global')) else None,
                'indic_enseig': float(row.get('indic_enseig')) if pd.notna(row.get('indic_enseig')) else None,
                'indic_env_rech': float(row.get('indic_env_rech')) if pd.notna(row.get('indic_env_rech')) else None,
                'indic_qualite_rech': float(row.get('indic_qualite_rech')) if pd.notna(row.get('indic_qualite_rech')) else None,
                'indic_impact_industrie': float(row.get('indic_impact_industrie')) if pd.notna(row.get('indic_impact_industrie')) else None,
                'indic_rel_intern': float(row.get('indic_rel_intern')) if pd.notna(row.get('indic_rel_intern')) else None,
                'ratio_fem': float(row.get('ratio_fem')) if pd.notna(row.get('ratio_fem')) else None,
                'ratio_hom': float(row.get('ratio_hom')) if pd.notna(row.get('ratio_hom')) else None,
            }
            
            classement_data = {k: v for k, v in classement_data.items() if v is not None}

            classement = Classement(**classement_data)
            db.session.add(classement)
            count += 1
            
            if count % 100 == 0:
                db.session.commit()
                logger.info(f"Commit intermédiaire après {count} classements ajoutés.")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout du classement pour {nom_univ} (ligne {index}): {e}")
            
    db.session.commit()
    logger.info(f"Peuplement de la table Classement terminé. {count} nouveaux enregistrements ajoutés.")


# Auteur : Romain Lesueur
def main():
    """Fonction principale pour initialiser l'application et peupler la base."""
    
    logger.info("=" * 60)
    logger.info("DEBUT DU PEUPLEMENT DE LA BASE DE DONNEES")
    logger.info("=" * 60)
    
    app = create_app("development")
    
    with app.app_context():
        logger.info("Reinitialisation des tables...")
        db.drop_all()
        db.create_all()
        logger.info("Tables de la base de données recréées.")

        csv_path = Config.CSV_FUSIONNE
        df = lire_csv(csv_path)
        
        if df is None:
            logger.error("Impossible de charger les données. Arret.")
            sys.exit(1)
            
        # 1. Peuplement des régions (Anthony YON)
        logger.info("-" * 40)
        logger.info("Insertion des regions...")
        regions_mapping  = peupler_regions(df)
        
        # 2. Peuplement des pays (Anthony YON)
        logger.info("-" * 40)
        logger.info("Insertion des pays...")
        pays_mapping = peupler_pays(df, regions_mapping)
        
        # 3. Peuplement des universités (Mandir)
        logger.info("-" * 40)
        logger.info("Insertion des universites...")
        univ_mapping = peupler_universites(df, regions_mapping)
        
        # 4. Peuplement des classements (Mandir)
        logger.info("-" * 40)
        logger.info("Insertion des classements...")
        peupler_classement(df, univ_mapping)
        
        # Resume final
        logger.info("=" * 60)
        logger.info("RESUME DU PEUPLEMENT")
        logger.info("=" * 60)
        logger.info(f"Regions:      {db.session.query(Region).count()}")
        logger.info(f"Pays:         {db.session.query(Pays).count()}")
        logger.info(f"Universites:  {db.session.query(Universite).count()}")
        logger.info(f"Classements:  {db.session.query(Classement).count()}")
        logger.info("=" * 60)
        logger.info("PEUPLEMENT TERMINE AVEC SUCCES")
        logger.info("=" * 60)

if __name__ == '__main__':
    main()