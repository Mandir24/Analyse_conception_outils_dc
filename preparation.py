#*************************************************************************#
# Auteur : DIOP MANDIR
# Date : Script de nettoyage et préparation des données
#*************************************************************************#
"""
Script de préparation des données des fichiers de données, 
notamment 'statistiques_pays_du_monde.csv' et
'Classement_THE_des_universites_mondiales_2016–2025.csv'.
"""
#===============================================================#
#================ Importation des bibliothèques ================#
#===============================================================#
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import logging
import os
from datetime import datetime

#===============================================================#
#================ Configuration du logging =====================#
#===============================================================#
def configurer_logger():
    """Configure le système de logging avec fichier et console."""
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nom du fichier de log avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/preparation_donnees_{timestamp}.log'
    
    # Configuration du logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

#===============================================================#
#================ Fonctions de traitement ======================#
#===============================================================#
def charger_fichier_csv(chemin, description, logger):
    """Charge un fichier CSV avec gestion d'erreurs."""
    logger.info(f"Lecture du fichier {description}...")
    print(f"\n Lecture du fichier {description}...")
    
    try:
        df = pd.read_csv(chemin)
        logger.info(f"✓ Fichier chargé avec succès : {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"  ✓ Fichier chargé avec succès")
        print(f"    Lignes : {len(df)} | Colonnes : {len(df.columns)}")
        return df
    except FileNotFoundError:
        logger.error(f"✗ Fichier introuvable : {chemin}")
        print(f"  ✗ ERREUR : Fichier '{chemin}' introuvable")
        raise
    except PermissionError:
        logger.error(f"✗ Permission refusée pour : {chemin}")
        print(f"  ✗ ERREUR : Permission refusée. Fermez le fichier s'il est ouvert.")
        raise
    except Exception as e:
        logger.error(f"✗ Erreur lors du chargement : {str(e)}")
        print(f"  ✗ ERREUR : {str(e)}")
        raise

def traiter_fichier_pays(df, logger):
    """Traite le fichier des statistiques pays."""
    logger.info("=== DÉBUT TRAITEMENT FICHIER PAYS ===")
    
    # 1. Conversion des colonnes numériques
    logger.info("Conversion des colonnes numériques...")
    print("\n Conversion des colonnes numériques...")
    
    cols_a_convert = [
        "Pop. Density (per sq. mi.)", "Coastline (coast/area ratio)",
        "Net migration", "Infant mortality (per 1000 births)",
        "Literacy (%)", "Phones (per 1000)", "Arable (%)",
        "Crops (%)", "Other (%)", "Birthrate", "Deathrate",
        "Agriculture", "Industry", "Service"
    ]
    
    for col in cols_a_convert:
        try:
            df[col] = df[col].str.replace(",", ".", regex=False).astype(float)
        except Exception as e:
            logger.warning(f"Problème conversion colonne {col}: {e}")
    
    logger.info("✓ Conversion terminée")
    print("  ✓ Conversion terminée")
    
    # 2. Vérification des doublons
    logger.info("Vérification des doublons...")
    print("\n Vérification des doublons...")
    nb_doublons = df.duplicated().sum()
    logger.info(f"Nombre de doublons trouvés : {nb_doublons}")
    print(f"  ✓ Doublons détectés : {nb_doublons}")
    
    # 3. Sélection des colonnes
    logger.info("Sélection des colonnes pertinentes...")
    print("\n Sélection des colonnes pertinentes...")
    
    cols_a_garder = [
        "Country", "Region", "Area (sq. mi.)", "Population",
        "Net migration", "GDP ($ per capita)", "Literacy (%)",
        "Phones (per 1000)", "Industry", "Service"
    ]
    
    df = df[cols_a_garder]
    logger.info(f"{len(cols_a_garder)} colonnes conservées")
    print(f"  ✓ {len(cols_a_garder)} colonnes conservées")
    
    # 4. Gestion des valeurs nulles
    logger.info("Gestion des valeurs nulles...")
    print("\n🧹 Gestion des valeurs nulles...")
    
    cols_isna = ["Net migration", "GDP ($ per capita)", "Literacy (%)",
                 "Phones (per 1000)", "Industry", "Service"]
    
    for col in cols_isna:
        nb_na = df[col].isna().sum()
        if nb_na > 0:
            logger.warning(f"Valeurs manquantes dans {col}: {nb_na}")
            print(f"    - {col}: {nb_na} valeurs manquantes")
            df[col] = df[col].fillna(df[col].median())
    
    logger.info("✓ Valeurs nulles traitées")
    print("  ✓ Valeurs nulles remplies avec la médiane")
    
    # 5. Nettoyage des espaces
    logger.info("Nettoyage des espaces...")
    print("\n✂️  Nettoyage des espaces...")
    
    cols_str = ["Country", "Region"]
    for col in cols_str:
        df[col] = df[col].astype(str).str.strip()
    
    logger.info("✓ Espaces supprimés")
    print("  ✓ Espaces supprimés")
    
    # 6. Renommage des colonnes
    logger.info("Renommage des colonnes...")
    print("\n  Renommage des colonnes...")
    
    df.rename(columns={
        "Country": "pays",
        "Region": "region",
        "Area (sq. mi.)": "superf_m2",
        "Population": "population",
        "Net migration": "migration_nette",
        "GDP ($ per capita)": "pib_hab",
        "Literacy (%)": "alphabetisation_pct",
        "Phones (per 1000)": "tel_1000hab",
        "Industry": "industrie_part",
        "Service": "services_part"
    }, inplace=True)
    
    logger.info("✓ Colonnes renommées")
    print("  ✓ Colonnes renommées")
    
    logger.info("=== FIN TRAITEMENT FICHIER PAYS ===")
    return df

def extraire_ratios(valeur):
    """
    Extrait ratio femme/homme.
    Retourne : (ratio_fem_pct, ratio_hom_pct)
    """
    if pd.isnull(valeur) or valeur == '':
        return None, None
    
    try:
        valeur_str = str(valeur).strip()
        
        # Format décimal (0.45)
        if valeur_str.replace('.', '', 1).isdigit():
            dec = float(valeur_str)
            if 0 <= dec <= 1:
                fem = round(dec * 100, 2)
                hom = round(100 - fem, 2)
                return fem, hom
        
        # Format "45:55"
        if ":" in valeur_str:
            parts = valeur_str.split(':')
            if len(parts) >= 2:
                fem = float(parts[0])
                hom = float(parts[1])
                total = fem + hom
                if total > 0:
                    fem_pct = round(fem / total * 100, 2)
                    hom_pct = round(100 - fem_pct, 2)
                    return fem_pct, hom_pct
    except:
        pass
    
    return None, None

def detecter_valeurs_aberrantes(df, colonne, logger):
    """Détecte les valeurs aberrantes avec la méthode IQR."""
    Q1 = df[colonne].quantile(0.25)
    Q3 = df[colonne].quantile(0.75)
    IQR = Q3 - Q1
    seuil_bas = Q1 - 1.5 * IQR
    seuil_haut = Q3 + 1.5 * IQR
    
    aberrantes = df[(df[colonne] < seuil_bas) | (df[colonne] > seuil_haut)]
    
    if len(aberrantes) > 0:
        logger.info(f"Outliers détectés dans {colonne}: {len(aberrantes)}")
    
    return aberrantes

def traiter_fichier_classement(data, logger):
    """Traite le fichier de classement THE."""
    logger.info("=== DÉBUT TRAITEMENT FICHIER CLASSEMENT ===")
    
    # 1. Correction des types
    logger.info("Correction des types de données...")
    print("\n Correction des types de données...")
    
    data['International Students'] = data['International Students'].str.replace('%', '', regex=False)
    
    def convertion_colonne_int(colonne):
        return pd.to_numeric(colonne, errors='coerce').astype('Int64')
    
    liste_colonnes_int = ['Rank', 'Student Population', 'Year']
    for col in liste_colonnes_int:
        data[col] = convertion_colonne_int(data[col])
    
    logger.info("✓ Types corrigés")
    print("  ✓ Types corrigés")
    
    # 2. Extraction des ratios
    logger.info("Extraction des ratios Femme/Homme...")
    print("\n Extraction des ratios Femme/Homme...")
    
    # Extraction des ratios
    data[['ratio_fem', 'ratio_hom']] = data['Female to Male Ratio'].apply(
        lambda x: pd.Series(extraire_ratios(x))
    )
    
    # Calcul du ratio fem/hom
    data['ratio_fem_hom'] = data.apply(
        lambda row: round(row['ratio_fem'] / row['ratio_hom'], 2)
        if pd.notnull(row['ratio_fem']) and pd.notnull(row['ratio_hom']) and row['ratio_hom'] != 0
        else None,
        axis=1
    )
    
    # Suppression de la colonne originale Female to Male Ratio
    data = data.drop(columns=['Female to Male Ratio'])
    
    logger.info("✓ Ratios extraits")
    print("  ✓ Ratios extraits (ratio_fem, ratio_hom, ratio_fem_hom conservés)")
    print("  ✓ Colonne 'Female to Male Ratio' supprimée")
    
    # 3. Renommage
    logger.info("Renommage des colonnes...")
    print("\n  Renommage des colonnes...")
    
    noms_colonnes = {
        'Rank': 'rang',
        'Name': 'nom_univ',
        'Country': 'pays',
        'Student Population': 'pop_etud',
        'Students to Staff Ratio': 'ratio_etud_pers',
        'International Students': 'etud_internationaux_pct',
        'Overall Score': 'score_global',
        'Teaching': 'indic_enseig',
        'Research Environment': 'indic_env_rech',
        'Research Quality': 'indic_qualite_rech',
        'Industry Impact': 'indic_impact_industrie',
        'International Outlook': 'indic_rel_intern',
        'Year': 'annee'
    }
    data.rename(columns=noms_colonnes, inplace=True)
    
    logger.info("✓ Colonnes renommées")
    print("  ✓ Colonnes renommées")
    
    # 4. Détection des outliers
    logger.info("Détection des outliers...")
    print("\n Détection des outliers (Méthode IQR)...")
    
    colonnes_numeriques = [
        'rang', 'pop_etud', 'ratio_etud_pers', 'score_global',
        'indic_enseig', 'indic_env_rech', 'indic_qualite_rech',
        'indic_impact_industrie', 'indic_rel_intern'
    ]
    
    for col in colonnes_numeriques:
        aberrantes = detecter_valeurs_aberrantes(data, col, logger)
        print(f"    - {col}: {len(aberrantes)} outliers")
    
    logger.info("✓ Détection terminée")
    print("  ✓ Détection terminée")
    
    logger.info("=== FIN TRAITEMENT FICHIER CLASSEMENT ===")
    return data

def analyser_et_fusionner_donnees(data_pays, data_classement, logger):
    """Analyse les différences et fusionne les données."""
    logger.info("=== DÉBUT ANALYSE ET FUSION ===")
    
    # 1. Mapping des pays
    logger.info("Application du mapping des pays...")
    print("\n  Mapping des pays...")
    
    mapping_pays = {
        'Bosnia & Herzegovina': 'Bosnia and Herzegovina',
        'Brunei': 'Brunei Darussalam',
        'Congo, Dem. Rep.': 'Democratic Republic of the Congo',
        'Korea, South': 'South Korea',
        'Macau': 'Macao',
        'Macedonia': 'North Macedonia',
        'Russia': 'Russian Federation',
        'Gaza Strip': 'Palestine',
        'West Bank': 'Palestine',
    }
    
    data_pays['pays'] = data_pays['pays'].replace(mapping_pays)
    logger.info("✓ Mapping appliqué")
    print("  ✓ Mapping appliqué")
    
    # 2. Suppression des doublons
    logger.info("Vérification des doublons...")
    print("\n Vérification des doublons...")
    
    doublons = data_pays['pays'].value_counts()
    nb_doublons = len(doublons[doublons > 1])
    
    if nb_doublons > 0:
        logger.warning(f"{nb_doublons} pays en double détectés")
        print(f"    {nb_doublons} pays en double détectés")
        data_pays_clean = data_pays.drop_duplicates(subset=['pays'])
        logger.info("Doublons supprimés")
        print(f"  ✓ Doublons supprimés")
    else:
        data_pays_clean = data_pays
        logger.info("Aucun doublon")
        print("  ✓ Aucun doublon détecté")
    
    # 3. Analyse des pays
    logger.info("Analyse des pays communs et manquants...")
    print("\n Analyse des pays communs et manquants...")
    
    pays_classement = set(data_classement['pays'].dropna().unique())
    pays_data = set(data_pays_clean['pays'].dropna().unique())
    pays_manquants_data = pays_classement - pays_data
    pays_communs = pays_classement & pays_data
    
    logger.info(f"Pays dans classement: {len(pays_classement)}")
    logger.info(f"Pays dans data_pays: {len(pays_data)}")
    logger.info(f"Pays en commun: {len(pays_communs)}")
    print(f"  • Pays classement: {len(pays_classement)}")
    print(f"  • Pays data_pays: {len(pays_data)}")
    print(f"  • Pays communs: {len(pays_communs)}")
    
    if pays_manquants_data:
        logger.warning(f"{len(pays_manquants_data)} pays manquants dans data_pays")
        print(f"\n⚠️  Pays manquants dans data_pays ({len(pays_manquants_data)}):")
        for pays in sorted(pays_manquants_data):
            nb_univ = len(data_classement[data_classement['pays'] == pays])
            logger.warning(f"  - {pays}: {nb_univ} université(s)")
            print(f"     • {pays} ({nb_univ} université(s))")
    
    # 4. Fusion
    logger.info("Fusion des dataframes...")
    print("\n🔗 Fusion des données...")
    
    data_final = data_classement.merge(
        data_pays_clean,
        on='pays',
        how='left',
        suffixes=('', '_pays')
    )
    
    logger.info(f"Fusion effectuée: {len(data_final)} lignes")
    print(f"  ✓ Fusion effectuée: {len(data_final)} lignes")
    
    # 5. Traitement des régions manquantes
    logger.info("Traitement des régions manquantes...")
    print("\n Traitement des régions manquantes...")
    
    if 'region' in data_final.columns:
        nb_manquantes = data_final['region'].isna().sum()
        logger.info(f"Régions manquantes: {nb_manquantes}")
        print(f"  • Régions manquantes: {nb_manquantes}")
        
        data_final['region'] = data_final['region'].fillna('Inconnu')
        data_final['region'] = data_final['region'].replace(['', ' '], 'Inconnu')
        
        logger.info("✓ Régions traitées")
        print("  ✓ Régions traitées")
    
    logger.info("=== FIN ANALYSE ET FUSION ===")
    return data_pays_clean, data_final, pays_manquants_data

def sauvegarder_fichiers(data_pays, data_classement, data_final, pays_manquants, logger):
    """Sauvegarde tous les fichiers de sortie."""
    logger.info("=== DÉBUT SAUVEGARDE FICHIERS ===")
    print("\n Sauvegarde des fichiers...")
    
    fichiers_sauvegardes = []
    
    try:
        # Créer le dossier si nécessaire
        os.makedirs('data', exist_ok=True)
        
        # 1. data_pays.csv
        chemin = 'data/data_pays.csv'
        data_pays.to_csv(chemin, index=False)
        logger.info(f"✓ Fichier sauvegardé: {chemin}")
        print(f"  ✓ {chemin}")
        fichiers_sauvegardes.append(chemin)
        
        # 2. Classement nettoyé
        chemin = 'data/Classement_THE_nettoye.csv'
        data_classement.to_csv(chemin, index=False)
        logger.info(f"✓ Fichier sauvegardé: {chemin}")
        print(f"  ✓ {chemin}")
        fichiers_sauvegardes.append(chemin)
        
        # 3. data_final_fusionne.csv
        chemin = 'data/data_final_fusionne.csv'
        data_final.to_csv(chemin, index=False)
        logger.info(f"✓ Fichier sauvegardé: {chemin}")
        print(f"  ✓ {chemin}")
        fichiers_sauvegardes.append(chemin)
        
        # 4. Rapport pays manquants
        if pays_manquants:
            detail_manquants = []
            for pays in sorted(pays_manquants):
                universites = data_classement[data_classement['pays'] == pays]['nom_univ'].tolist()
                detail_manquants.append({
                    'pays': pays,
                    'nb_universites': len(universites),
                    'universites': ' | '.join(universites)
                })
            
            df_detail = pd.DataFrame(detail_manquants)
            chemin = 'data/detail_pays_manquants.csv'
            df_detail.to_csv(chemin, index=False)
            logger.info(f"✓ Fichier sauvegardé: {chemin}")
            print(f"  ✓ {chemin}")
            fichiers_sauvegardes.append(chemin)
        
        logger.info(f"=== FIN SAUVEGARDE: {len(fichiers_sauvegardes)} fichiers ===")
        return fichiers_sauvegardes
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
        print(f"  ✗ ERREUR: {str(e)}")
        raise

#===============================================================#
#===================== FONCTION MAIN ===========================#
#===============================================================#
def main():
    """Fonction principale du script."""
    # Configuration du logger
    logger = configurer_logger()
    
    logger.info("="*70)
    logger.info("DÉMARRAGE DU SCRIPT DE NETTOYAGE DES DONNÉES")
    logger.info("="*70)
    
    print("\n" + "="*70)
    print("  SCRIPT DE NETTOYAGE ET PRÉPARATION DES DONNÉES")
    print("="*70)
    
    try:
        # PARTIE 1 : Traitement fichier pays
        logger.info("\n### PARTIE 1: TRAITEMENT FICHIER PAYS ###")
        print("\n" + "="*70)
        print("PARTIE 1 : TRAITEMENT FICHIER PAYS")
        print("="*70)
        
        df_pays = charger_fichier_csv(
            "data/statistiques_pays_du_monde.csv",
            "statistiques_pays_du_monde.csv",
            logger
        )
        df_pays = traiter_fichier_pays(df_pays, logger)
        
        # PARTIE 2 : Traitement fichier classement
        logger.info("\n### PARTIE 2: TRAITEMENT FICHIER CLASSEMENT ###")
        print("\n" + "="*70)
        print("PARTIE 2 : TRAITEMENT FICHIER CLASSEMENT THE")
        print("="*70)
        
        df_classement = charger_fichier_csv(
            "data/Classement_THE_des_universites_mondiales_2016–2025.csv",
            "Classement THE 2016-2025",
            logger
        )
        df_classement = traiter_fichier_classement(df_classement, logger)
        
        # PARTIE 3 : Analyse et fusion
        logger.info("\n### PARTIE 3: ANALYSE ET FUSION ###")
        print("\n" + "="*70)
        print("PARTIE 3 : ANALYSE ET FUSION DES DONNÉES")
        print("="*70)
        
        df_pays_clean, df_final, pays_manquants = analyser_et_fusionner_donnees(
            df_pays, df_classement, logger
        )
        
        # PARTIE 4 : Sauvegarde
        logger.info("\n### PARTIE 4: SAUVEGARDE ###")
        print("\n" + "="*70)
        print("PARTIE 4 : SAUVEGARDE DES FICHIERS")
        print("="*70)
        
        fichiers = sauvegarder_fichiers(
            df_pays_clean, df_classement, df_final, pays_manquants, logger
        )
        
        # Statistiques finales
        print("\n" + "="*70)
        print(" STATISTIQUES FINALES")
        print("="*70)
        print(f"\n  Répartition par région:")
        regions = df_final['region'].value_counts()
        for region, count in regions.items():
            print(f"    • {region}: {count} universités")
        
        logger.info("="*70)
        logger.info("✓ SCRIPT TERMINÉ AVEC SUCCÈS")
        logger.info("="*70)
        
        print("\n" + "="*70)
        print(" SCRIPT TERMINÉ AVEC SUCCÈS")
        print("="*70)
        print(f"\n {len(fichiers)} fichiers générés")
        print(f" Log sauvegardé dans le dossier 'logs/'")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"ERREUR CRITIQUE: {str(e)}", exc_info=True)
        print(f"\n ERREUR CRITIQUE: {str(e)}")
        print("Consultez le fichier de log pour plus de détails.")
        raise

#===============================================================#
#=================== POINT D'ENTRÉE ============================#
#===============================================================#
if __name__ == "__main__":
    main()