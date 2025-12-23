"""
Script de nettoyage et de fusion des données THE et statistiques pays.

Ce script fusionne les données du classement THE des universités mondiales
avec les statistiques socio-économiques des pays pour créer un fichier unique.

Auteur: Mandir Diop - Romain Lesueur
Date: Novembre 2025
"""

import pandas as pd
import numpy as np
import os
import sys
import logging
from typing import Tuple, Optional

# Configuration du logging (force UTF-8 pour le fichier de log)
file_handler = logging.FileHandler('data_cleaning.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# Réinitialiser handlers éventuels pour éviter doublons (utile si importé plusieurs fois)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)


def verifier_fichier(chemin: str) -> bool:
    """
    Vérifie l'existence et l'accessibilité d'un fichier.

    Args:
        chemin: Chemin du fichier à vérifier

    Returns:
        True si le fichier existe et est accessible, False sinon
    """
    if not os.path.exists(chemin):
        logger.error(f"Erreur : Le fichier '{chemin}' n'existe pas.")
        return False

    if not os.path.isfile(chemin):
        logger.error(f"Erreur : '{chemin}' n'est pas un fichier.")
        return False

    if not os.access(chemin, os.R_OK):
        logger.error(f"Erreur : Pas de permission de lecture pour '{chemin}'.")
        return False

    logger.info(f"Fichier '{chemin}' vérifié avec succès.")
    return True


def charger_fichier_the(chemin: str) -> Optional[pd.DataFrame]:
    """
    Charge et nettoie le fichier du classement THE.

    Args:
        chemin: Chemin du fichier CSV THE

    Returns:
        DataFrame nettoyé ou None en cas d'erreur
    """
    try:
        logger.info(f"Chargement du fichier THE : {chemin}")
        df = pd.read_csv(chemin, encoding='utf-8')

        logger.info(f"Fichier THE chargé : {len(df)} lignes, {len(df.columns)} colonnes")

        # Renommer les colonnes selon la nomenclature demandée
        renommage = {
            'Rank': 'rang',
            'Name': 'nom_univ',
            'Country': 'pays',
            'Student Population': 'pop_etud',
            'Students to Staff Ratio': 'ratio_etud_pers',
            'International Students': 'etud_internationaux_pct',
            'Female to Male Ratio': 'ratio_fem_hom',
            'Overall Score': 'score_global',
            'Teaching': 'indic_enseig',
            'Research Environment': 'indic_env_rech',
            'Research Quality': 'indic_qualite_rech',
            'Industry Impact': 'indic_impact_industrie',
            'International Outlook': 'indic_rel_intern',
            'Year': 'annee'
        }

        df = df.rename(columns=renommage)

        # Nettoyer les données
        logger.info("Nettoyage des données THE...")

        # 1. Nettoyer le pourcentage d'étudiants internationaux
        df['etud_internationaux_pct'] = df['etud_internationaux_pct'].astype(str).str.replace('%', '').str.strip()
        df['etud_internationaux_pct'] = pd.to_numeric(df['etud_internationaux_pct'], errors='coerce')

        # 2. Traiter le ratio femmes/hommes
        def extraire_ratio_fem_hom(ratio_str):
            """Extrait les ratios femmes et hommes depuis la chaîne."""
            if pd.isna(ratio_str) or ratio_str == '':
                return pd.Series({'ratio_fem': np.nan, 'ratio_hom': np.nan})

            # Format : "33 : 67" ou "46:54:00"
            ratio_str = str(ratio_str).replace(' ', '')
            parties = ratio_str.split(':')

            if len(parties) >= 2:
                try:
                    fem = float(parties[0])
                    hom = float(parties[1])
                    return pd.Series({'ratio_fem': fem, 'ratio_hom': hom})
                except (ValueError, IndexError):
                    return pd.Series({'ratio_fem': np.nan, 'ratio_hom': np.nan})

            return pd.Series({'ratio_fem': np.nan, 'ratio_hom': np.nan})

        ratios = df['ratio_fem_hom'].apply(extraire_ratio_fem_hom)
        df['ratio_fem'] = ratios['ratio_fem']
        df['ratio_hom'] = ratios['ratio_hom']

        # 3. Nettoyer les noms de pays (supprimer espaces superflus)
        df['pays'] = df['pays'].str.strip()

        # 4. Convertir les types numériques
        colonnes_numeriques = [
            'rang', 'pop_etud', 'ratio_etud_pers', 'score_global',
            'indic_enseig', 'indic_env_rech', 'indic_qualite_rech',
            'indic_impact_industrie', 'indic_rel_intern', 'annee'
        ]

        for col in colonnes_numeriques:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        logger.info(f"Données THE nettoyées : {len(df)} lignes conservées")
        logger.info(f"Années présentes : {sorted(df['annee'].dropna().unique())}")
        logger.info(f"Nombre de pays : {df['pays'].nunique()}")

        return df

    except FileNotFoundError:
        logger.error(f"Erreur : Fichier '{chemin}' introuvable.")
        return None
    except pd.errors.EmptyDataError:
        logger.error(f"Erreur : Le fichier '{chemin}' est vide.")
        return None
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier THE : {str(e)}")
        return None


def charger_fichier_pays(chemin: str) -> Optional[pd.DataFrame]:
    """
    Charge et nettoie le fichier des statistiques pays.

    Args:
        chemin: Chemin du fichier CSV pays

    Returns:
        DataFrame nettoyé ou None en cas d'erreur
    """
    try:
        logger.info(f"Chargement du fichier pays : {chemin}")
        df = pd.read_csv(chemin, encoding='utf-8')

        logger.info(f"Fichier pays chargé : {len(df)} lignes, {len(df.columns)} colonnes")

        # Renommer les colonnes
        renommage = {
            'Country': 'pays',
            'Region': 'region',
            'Population': 'population',
            'Area (sq. mi.)': 'superf_m2',
            'Net migration': 'migration_nette',
            'GDP ($ per capita)': 'pib_hab',
            'Literacy (%)': 'alphabetisation_pct',
            'Phones (per 1000)': 'tel_1000hab',
            'Industry': 'industrie_part',
            'Service': 'services_part'
        }

        df = df.rename(columns=renommage)

        # Nettoyer les données
        logger.info("Nettoyage des données pays...")

        # 1. Nettoyer les noms de pays (supprimer espaces et guillemets)
        df['pays'] = df['pays'].str.strip().str.replace('"', '').str.strip()
        df['region'] = df['region'].str.strip().str.replace('"', '').str.strip()

        # 2. Nettoyer les valeurs numériques avec virgule
        def nettoyer_nombre(valeur):
            """Convertit une chaîne avec virgule en nombre."""
            if pd.isna(valeur):
                return np.nan
            valeur = str(valeur).replace(',', '.').strip()
            try:
                return float(valeur)
            except ValueError:
                return np.nan

        colonnes_numeriques = [
            'population', 'superf_m2', 'migration_nette', 'pib_hab',
            'alphabetisation_pct', 'tel_1000hab', 'industrie_part', 'services_part'
        ]

        for col in colonnes_numeriques:
            if col in df.columns:
                df[col] = df[col].apply(nettoyer_nombre)

        # 3. Sélectionner uniquement les colonnes nécessaires
        colonnes_a_garder = ['pays', 'region', 'population', 'superf_m2', 'pib_hab',
                             'migration_nette', 'industrie_part', 'services_part',
                             'alphabetisation_pct', 'tel_1000hab']

        df = df[colonnes_a_garder]

        logger.info(f"Données pays nettoyées : {len(df)} pays")
        logger.info(f"Régions présentes : {df['region'].nunique()}")

        return df

    except FileNotFoundError:
        logger.error(f"Erreur : Fichier '{chemin}' introuvable.")
        return None
    except pd.errors.EmptyDataError:
        logger.error(f"Erreur : Le fichier '{chemin}' est vide.")
        return None
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier pays : {str(e)}")
        return None


def detecter_valeurs_aberrantes(df: pd.DataFrame, colonne: str) -> Tuple[pd.DataFrame, dict]:
    """
    Detecte les valeurs aberrantes dans une colonne en utilisant la methode IQR.

    Args:
        df: DataFrame a analyser
        colonne: Nom de la colonne a verifier

    Returns:
        Tuple (DataFrame des lignes aberrantes, dict avec statistiques IQR)
    """
    stats = {
        'Q1': None, 'Q3': None, 'IQR': None,
        'seuil_bas': None, 'seuil_haut': None,
        'min': None, 'max': None, 'median': None
    }

    if colonne not in df.columns:
        logger.warning(f"Colonne '{colonne}' non trouvee dans le DataFrame")
        return pd.DataFrame(), stats

    # Ignorer les valeurs NaN pour le calcul
    valeurs_valides = df[colonne].dropna()
    if len(valeurs_valides) == 0:
        return pd.DataFrame(), stats

    Q1 = valeurs_valides.quantile(0.25)
    Q3 = valeurs_valides.quantile(0.75)
    IQR = Q3 - Q1
    seuil_bas = Q1 - 1.5 * IQR
    seuil_haut = Q3 + 1.5 * IQR

    stats = {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'seuil_bas': seuil_bas,
        'seuil_haut': seuil_haut,
        'min': valeurs_valides.min(),
        'max': valeurs_valides.max(),
        'median': valeurs_valides.median()
    }

    # Separer outliers bas et hauts
    outliers_bas = df[df[colonne] < seuil_bas]
    outliers_hauts = df[df[colonne] > seuil_haut]
    aberrantes = pd.concat([outliers_bas, outliers_hauts])

    stats['nb_outliers_bas'] = len(outliers_bas)
    stats['nb_outliers_hauts'] = len(outliers_hauts)

    return aberrantes, stats


def analyser_outliers(df: pd.DataFrame, colonnes: list) -> dict:
    """
    Analyse detaillee des valeurs aberrantes pour plusieurs colonnes.

    Args:
        df: DataFrame a analyser
        colonnes: Liste des colonnes numeriques a verifier

    Returns:
        Dictionnaire avec les statistiques detaillees des outliers par colonne
    """
    logger.info("=" * 70)
    logger.info("DETECTION DES VALEURS ABERRANTES (methode IQR)")
    logger.info("=" * 70)

    resultats = {}
    total_outliers = 0

    for col in colonnes:
        if col not in df.columns:
            continue

        aberrantes, stats = detecter_valeurs_aberrantes(df, col)
        nb_aberrantes = len(aberrantes)
        total_outliers += nb_aberrantes

        resultats[col] = {
            'nombre': nb_aberrantes,
            'stats': stats,
            'indices': aberrantes.index.tolist() if not aberrantes.empty else []
        }

        if nb_aberrantes > 0:
            logger.info(f"")
            logger.info(f"Colonne '{col}' : {nb_aberrantes} valeur(s) aberrante(s)")
            logger.info(f"  Statistiques IQR :")
            logger.info(f"    - Q1 (25%) : {stats['Q1']:.2f}")
            logger.info(f"    - Mediane  : {stats['median']:.2f}")
            logger.info(f"    - Q3 (75%) : {stats['Q3']:.2f}")
            logger.info(f"    - IQR      : {stats['IQR']:.2f}")
            logger.info(f"  Seuils de detection :")
            logger.info(f"    - Seuil bas  : {stats['seuil_bas']:.2f}")
            logger.info(f"    - Seuil haut : {stats['seuil_haut']:.2f}")
            logger.info(f"  Valeurs reelles :")
            logger.info(f"    - Min : {stats['min']:.2f}")
            logger.info(f"    - Max : {stats['max']:.2f}")
            logger.info(f"  Repartition des outliers :")
            logger.info(f"    - Outliers bas (< {stats['seuil_bas']:.2f})  : {stats['nb_outliers_bas']}")
            logger.info(f"    - Outliers hauts (> {stats['seuil_haut']:.2f}) : {stats['nb_outliers_hauts']}")

            # Afficher quelques exemples d'universites avec outliers
            if 'nom_univ' in df.columns and not aberrantes.empty:
                logger.info(f"  Exemples d'universites concernees (max 5) :")
                sample = aberrantes.head(5)
                for idx, row in sample.iterrows():
                    nom = row.get('nom_univ', 'N/A')
                    pays = row.get('pays', 'N/A')
                    valeur = row[col]
                    logger.info(f"    - {nom} ({pays}) : {valeur}")
        else:
            logger.info(f"Colonne '{col}' : aucune valeur aberrante")

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"RESUME : Total des valeurs aberrantes detectees : {total_outliers}")
    logger.info("=" * 70)
    logger.info("=" * 70)

    return resultats


def analyser_pays_non_communs(df_the: pd.DataFrame, df_pays: pd.DataFrame) -> dict:
    """
    Analyse detaillee des pays non communs entre les deux fichiers.

    Args:
        df_the: DataFrame du classement THE
        df_pays: DataFrame des statistiques pays

    Returns:
        Dictionnaire avec les resultats de l'analyse
    """
    logger.info("=" * 70)
    logger.info("ANALYSE DES PAYS NON COMMUNS ENTRE LES DEUX FICHIERS")
    logger.info("=" * 70)

    # Ensemble des pays uniques dans chaque fichier
    pays_classement = set(df_the['pays'].dropna().unique())
    pays_data = set(df_pays['pays'].dropna().unique())

    # Calcul des ensembles
    pays_manquants_data = pays_classement - pays_data
    pays_manquants_classement = pays_data - pays_classement
    pays_communs = pays_classement & pays_data

    # Statistiques generales
    logger.info("STATISTIQUES GENERALES :")
    logger.info(f"  - Nombre de pays dans classement : {len(pays_classement)}")
    logger.info(f"  - Nombre de pays dans data_pays : {len(pays_data)}")
    logger.info(f"  - Nombre de pays en commun : {len(pays_communs)}")

    # Pays dans classement mais pas dans data_pays
    logger.info(f"PAYS DANS CLASSEMENT MAIS PAS DANS DATA_PAYS ({len(pays_manquants_data)}) :")
    if pays_manquants_data:
        for pays in sorted(pays_manquants_data):
            nb_univ = len(df_the[df_the['pays'] == pays])
            logger.info(f"  - {pays} ({nb_univ} universite(s))")
    else:
        logger.info("  Aucun")

    # Pays dans data_pays mais pas dans classement
    logger.info(f"PAYS DANS DATA_PAYS MAIS PAS DANS CLASSEMENT ({len(pays_manquants_classement)}) :")
    if pays_manquants_classement:
        for pays in sorted(pays_manquants_classement):
            logger.info(f"  - {pays}")
    else:
        logger.info("  Aucun")

    # Impact sur la fusion
    logger.info("=" * 70)
    logger.info("IMPACT SUR LA FUSION")
    logger.info("=" * 70)

    nb_univ_sans_data = df_the[df_the['pays'].isin(pays_manquants_data)].shape[0]
    total_univ = len(df_the)
    pourcentage = (nb_univ_sans_data / total_univ) * 100 if total_univ > 0 else 0

    logger.warning(f"{nb_univ_sans_data} universites sur {total_univ} ({pourcentage:.2f}%) "
                   f"n'auront pas de donnees pays apres la fusion.")

    # Detail par pays manquant
    if pays_manquants_data:
        logger.info("DETAIL DES UNIVERSITES SANS DONNEES PAYS :")
        for pays in sorted(pays_manquants_data):
            nb = len(df_the[df_the['pays'] == pays])
            logger.info(f"  - {pays}: {nb} universite(s)")

    logger.info("=" * 70)

    return {
        'pays_classement': pays_classement,
        'pays_data': pays_data,
        'pays_manquants_data': pays_manquants_data,
        'pays_manquants_classement': pays_manquants_classement,
        'pays_communs': pays_communs,
        'nb_univ_sans_data': nb_univ_sans_data,
        'pourcentage_perte': pourcentage
    }


def normaliser_noms_pays(df_the: pd.DataFrame, df_pays: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Normalise les noms de pays entre les deux fichiers pour faciliter la fusion.

    Args:
        df_the: DataFrame THE
        df_pays: DataFrame pays

    Returns:
        Tuple des deux DataFrames avec noms de pays normalises
    """
    logger.info("Normalisation des noms de pays...")

    # Mapping des noms de pays différents (étendre les cas rencontrés)
    mapping_pays = {
        'United States': 'United States',
        'United Kingdom': 'United Kingdom',
        'USA': 'United States',
        'UK': 'United Kingdom',
        'Bosnia and Herzegovina': 'Bosnia & Herzegovina',
        'Brunei Darussalam': 'Brunei',
        'Democratic Republic of the Congo': 'Congo, Dem. Rep.',
        'Republic of the Congo': 'Congo, Repub. of the',
        'North Macedonia': 'Macedonia',
        'Macedonia (FYROM)': 'Macedonia',
        'Macao': 'Macau',
        'Russian Federation': 'Russia',
        'Northern Cyprus': 'Cyprus',
        'South Korea': 'Korea, South'
        # 'Kosovo', 'Montenegro', 'Palestine' Pas de correspondance dans les statistiques pays
    }

    def _normalize_name(n):
        if pd.isna(n) or not str(n).strip():
            return n
        s = str(n).strip()
        if s in mapping_pays:
            return mapping_pays[s]
        alt = s.replace(' and ', ' & ')
        if alt in mapping_pays:
            return mapping_pays[alt]
        low = s.lower()
        if 'democratic' in low and 'congo' in low:
            return mapping_pays.get('Democratic Republic of the Congo', s)
        if 'russian' in low or 'federation' in low:
            return mapping_pays.get('Russian Federation', s)
        if 'macao' in low:
            return mapping_pays.get('Macao', s)
        return s

    # Appliquer le mapping sur les deux dataframes
    df_the['pays'] = df_the['pays'].apply(_normalize_name)
    df_pays['pays'] = df_pays['pays'].apply(_normalize_name)

    # Vérifier les pays manquants
    pays_the = set(df_the['pays'].unique())
    pays_stats = set(df_pays['pays'].unique())

    pays_manquants = pays_the - pays_stats
    if pays_manquants:
        logger.warning(f"{len(pays_manquants)} pays du fichier THE n'ont pas de statistiques : {sorted(list(pays_manquants))[:10]}...")

    return df_the, df_pays


def fusionner_donnees(df_the: pd.DataFrame, df_pays: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Fusionne les donnees THE et pays en un seul DataFrame.
    Inclut l'analyse des pays non communs et la detection des outliers.

    Args:
        df_the: DataFrame THE nettoye
        df_pays: DataFrame pays nettoye

    Returns:
        DataFrame fusionne ou None en cas d'erreur
    """
    try:
        logger.info("Fusion des donnees...")

        # Normaliser les noms de pays
        df_the, df_pays = normaliser_noms_pays(df_the, df_pays)

        # Analyse detaillee des pays non communs avant fusion
        analyse_pays = analyser_pays_non_communs(df_the, df_pays)

        # Fusion sur le nom du pays (LEFT JOIN pour conserver toutes les universites)
        df_fusionne = pd.merge(
            df_the,
            df_pays,
            on='pays',
            how='left'
        )

        logger.info(f"Fusion reussie : {len(df_fusionne)} lignes")

        # Detection des outliers sur les colonnes numeriques
        colonnes_outliers = [
            'rang', 'pop_etud', 'ratio_etud_pers', 'score_global',
            'indic_enseig', 'indic_env_rech', 'indic_qualite_rech',
            'indic_impact_industrie', 'indic_rel_intern',
            'population', 'pib_hab', 'alphabetisation_pct'
        ]
        resultats_outliers = analyser_outliers(df_fusionne, colonnes_outliers)

        # Ordonner les colonnes selon la spécification
        colonnes_ordre = [
            'rang', 'nom_univ', 'pays', 'pop_etud', 'ratio_etud_pers',
            'etud_internationaux_pct', 'ratio_fem_hom', 'score_global',
            'indic_enseig', 'indic_env_rech', 'indic_qualite_rech',
            'indic_impact_industrie', 'indic_rel_intern', 'annee',
            'ratio_fem', 'ratio_hom', 'region', 'population', 'superf_m2',
            'pib_hab', 'migration_nette', 'industrie_part', 'services_part',
            'alphabetisation_pct', 'tel_1000hab'
        ]

        # S'assurer que toutes les colonnes existent
        for col in colonnes_ordre:
            if col not in df_fusionne.columns:
                df_fusionne[col] = np.nan

        df_fusionne = df_fusionne[colonnes_ordre]

        # Afficher des statistiques finales
        logger.info("=" * 70)
        logger.info("STATISTIQUES FINALES")
        logger.info("=" * 70)
        logger.info(f"  - Lignes totales : {len(df_fusionne)}")
        logger.info(f"  - Universites uniques : {df_fusionne['nom_univ'].nunique()}")
        logger.info(f"  - Pays uniques : {df_fusionne['pays'].nunique()}")
        logger.info(f"  - Annees : {sorted(df_fusionne['annee'].dropna().unique())}")
        logger.info(f"  - Lignes avec donnees pays : {df_fusionne['region'].notna().sum()}")
        logger.info(f"  - Lignes sans donnees pays : {df_fusionne['region'].isna().sum()}")

        # Log du resume des pertes de donnees
        if analyse_pays['nb_univ_sans_data'] > 0:
            logger.warning("RESUME DES PERTES DE DONNEES :")
            logger.warning(f"  - {analyse_pays['nb_univ_sans_data']} lignes sans statistiques pays")
            logger.warning(f"  - Pays concernes : {', '.join(sorted(analyse_pays['pays_manquants_data']))}")

        return df_fusionne

    except Exception as e:
        logger.error(f"Erreur lors de la fusion des données : {str(e)}")
        return None


def sauvegarder_donnees(df: pd.DataFrame, chemin_sortie: str) -> bool:
    """
    Sauvegarde le DataFrame fusionné dans un fichier CSV.

    Args:
        df: DataFrame à sauvegarder
        chemin_sortie: Chemin du fichier de sortie

    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    try:
        logger.info(f"Sauvegarde des données dans '{chemin_sortie}'...")

        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)

        # Sauvegarder
        df.to_csv(chemin_sortie, index=False, encoding='utf-8')

        logger.info(f"Données sauvegardées avec succès ({len(df)} lignes)")
        return True

    except PermissionError:
        logger.error(f"Erreur : Pas de permission d'écriture pour '{chemin_sortie}'.")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde : {str(e)}")
        return False


def main():
    """Fonction principale du script."""
    logger.info("=" * 80)
    logger.info("Démarrage du nettoyage et de la fusion des données")
    logger.info("=" * 80)

    # Chemins des fichiers
    chemin_the = 'data/Classement_THE_des_universites_mondiales_2016–2025.csv'
    chemin_pays = 'data/statistiques_pays_du_monde.csv'
    chemin_sortie = 'data/donnees_fusionnees.csv'

    # Vérifier l'existence des fichiers
    if not verifier_fichier(chemin_the):
        sys.exit(1)

    if not verifier_fichier(chemin_pays):
        sys.exit(1)

    # Charger les fichiers
    df_the = charger_fichier_the(chemin_the)
    if df_the is None:
        logger.error("Échec du chargement du fichier THE. Arrêt du script.")
        sys.exit(1)

    df_pays = charger_fichier_pays(chemin_pays)
    if df_pays is None:
        logger.error("Échec du chargement du fichier pays. Arrêt du script.")
        sys.exit(1)

    # Fusionner les données
    df_fusionne = fusionner_donnees(df_the, df_pays)
    if df_fusionne is None:
        logger.error("Échec de la fusion des données. Arrêt du script.")
        sys.exit(1)

    # Sauvegarder
    if not sauvegarder_donnees(df_fusionne, chemin_sortie):
        logger.error("Échec de la sauvegarde. Arrêt du script.")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("Traitement terminé avec succès !")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
