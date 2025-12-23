#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de lancement automatique du projet World-Univ-Rank
Exécute toutes les étapes nécessaires pour démarrer l'application
"""

import os
import sys
import subprocess
from pathlib import Path
import venv

# Codes couleur pour le terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_step(step, message):
    """Affiche une étape avec son numéro"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Étape {step}]{Colors.ENDC} {message}")


def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")


def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.FAIL}{message}{Colors.ENDC}")


def print_info(message):
    """Affiche un message d'information"""
    print(f"{Colors.OKBLUE}{message}{Colors.ENDC}")


def setup_virtual_environment():
    """
    Détecte, crée ou active un environnement virtuel
    
    Returns:
        str: Chemin vers l'exécutable Python du venv
    """
    print_step("0", "Configuration de l'environnement virtuel")
    
    # Détecter le système d'exploitation
    import platform
    system = platform.system()
    
    venv_path = Path("venv")
    
    # Déterminer le chemin de l'exécutable Python dans le venv selon l'OS
    if system == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
        print_info(f"Système détecté : Windows")
    elif system == "Darwin":  # macOS
        venv_python = venv_path / "bin" / "python"
        print_info(f"Système détecté : macOS")
    else:  # Linux et autres
        venv_python = venv_path / "bin" / "python"
        print_info(f"Système détecté : {system}")
    
    # Vérifier si le venv existe déjà
    if venv_path.exists() and venv_python.exists():
        print_success(f"Environnement virtuel trouvé : {venv_path}")
        return str(venv_python)
    
    # Créer le venv s'il n'existe pas
    print_info(f"Création de l'environnement virtuel dans {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        
        # Vérifier que l'exécutable a bien été créé
        if not venv_python.exists():
            raise FileNotFoundError(f"L'exécutable Python n'a pas été créé : {venv_python}")
        
        print_success("Environnement virtuel créé avec succès")
        return str(venv_python)
    except Exception as e:
        print_error(f"Erreur lors de la création du venv : {str(e)}")
        print_info("Utilisation de l'interpréteur Python système")
        return sys.executable


def run_script(script_path, description):
    """
    Exécute un script Python et gère les erreurs
    
    Args:
        script_path: Chemin vers le script à exécuter
        description: Description de l'étape
    
    Returns:
        bool: True si succès, False sinon
    """
    try:
        print_info(f"Exécution de {script_path}...")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Afficher la sortie du script
        if result.stdout:
            print(result.stdout)
        
        print_success(f"{description} terminé avec succès")
        return True
    
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de {description}")
        print(f"\n{Colors.FAIL}Message d'erreur :{Colors.ENDC}")
        print(e.stderr if e.stderr else e.stdout)
        return False
    
    except FileNotFoundError:
        print_error(f"Script introuvable : {script_path}")
        return False


def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    print_step("1", "Vérification des dépendances")
    
    required_packages = ['flask', 'pandas', 'sqlalchemy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"Package '{package}' trouvé")
        except ImportError:
            missing_packages.append(package)
            print_error(f"Package '{package}' manquant")
    
    if missing_packages:
        print(f"\n{Colors.WARNING}Packages manquants détectés !{Colors.ENDC}")
        print_info("Installation automatique en cours...")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirement.txt"],
                check=True
            )
            print_success("Dépendances installées avec succès")
        except subprocess.CalledProcessError:
            print_error("Échec de l'installation des dépendances")
            print_info("Veuillez exécuter manuellement : pip install -r requirement.txt")
            return False
    
    return True


def main():
    """Fonction principale du script de lancement"""
    
    print_header(" LANCEMENT AUTOMATIQUE - WORLD-UNIV-RANK")
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path("application.py").exists():
        print_error("Erreur : application.py introuvable")
        print_info("Assurez-vous d'exécuter ce script depuis la racine du projet")
        sys.exit(1)
    
    # Configurer l'environnement virtuel
    venv_python = setup_virtual_environment()
    
    # Utiliser le Python du venv pour toutes les opérations suivantes
    original_executable = sys.executable
    sys.executable = venv_python
    
    print()  # Ligne vide pour la lisibilité
    
    # Vérifier les dépendances
    if not check_dependencies():
        print_error("Impossible de continuer sans les dépendances")
        sys.executable = original_executable
        sys.exit(1)
    
    print()  # Ligne vide pour la lisibilité
    
    # Étape 1 : Nettoyage des données
    print_step("2/4", "Nettoyage et fusion des données CSV")
    if not run_script("scripts/clean_data.py", "Nettoyage des données"):
        print_error("Échec du nettoyage des données")
        sys.executable = original_executable
        sys.exit(1)
    
    print()  # Ligne vide pour la lisibilité
    
    # Étape 2 : Peuplement de la base de données
    print_step("3/4", "Peuplement de la base de données SQLite")
    if not run_script("scripts/populate_db.py", "Peuplement de la base"):
        print_error("Échec du peuplement de la base de données")
        sys.executable = original_executable
        sys.exit(1)
    
    print()  # Ligne vide pour la lisibilité
    
    # Étape 3 : Lancement de l'application Flask
    print_step("4/4", "Lancement de l'application Flask")
    print_success("Tous les scripts ont été exécutés avec succès !")
    
    print_header(" DÉMARRAGE DU SERVEUR FLASK ")
    print_info("L'application va démarrer sur http://localhost:5000")
    print_info("Appuyez sur CTRL+C pour arrêter le serveur")
    print()
    
    try:
        # Lancer Flask directement (sans subprocess pour voir les logs en temps réel)
        subprocess.run([sys.executable, "application.py"], check=True)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Arrêt du serveur demandé par l'utilisateur{Colors.ENDC}")
        print_success("Application arrêtée proprement")
    except subprocess.CalledProcessError as e:
        print_error("Erreur lors du lancement de l'application")
        sys.executable = original_executable
        sys.exit(1)
    finally:
        sys.executable = original_executable


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"Erreur inattendue : {str(e)}")
        sys.exit(1)
