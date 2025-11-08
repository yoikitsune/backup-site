"""Module de gestion des configurations.

Ce module fournit des classes pour charger, valider et gérer les configurations
de sauvegarde au format YAML avec support des variables d'environnement.
"""

from pathlib import Path
from typing import Optional

from .models import SiteConfig, SSHConfig, FilesConfig, DatabaseConfig, BackupConfig


def load_config(config_path: Path) -> SiteConfig:
    """Charge et valide une configuration à partir d'un fichier YAML.
    
    Args:
        config_path: Chemin vers le fichier de configuration YAML
        
    Returns:
        Une instance de SiteConfig validée
        
    Raises:
        FileNotFoundError: Si le fichier de configuration n'existe pas
        ValueError: Si la configuration est invalide
    """
    return SiteConfig.from_yaml(config_path)


def create_default_config(destination: Path) -> None:
    """Crée un fichier de configuration par défaut.
    
    Args:
        destination: Chemin où enregistrer la configuration par défaut
    """
    from rich.console import Console
    from rich.syntax import Syntax
    
    console = Console()
    
    # Vérifie si le fichier existe déjà
    if destination.exists():
        console.print(f"[yellow]Attention: Le fichier {destination} existe déjà."
                    " Voulez-vous le remplacer ? (o/N)")
        if input().lower() != 'o':
            console.print("Annulé.")
            return
    
    # Chemin vers le fichier d'exemple à la racine du projet
    # On utilise 4 niveaux de parent pour remonter de src/backup_site/config/ à la racine
    example_path = Path(__file__).resolve().parents[3] / "example-site.yaml"
    
    if not example_path.exists():
        raise FileNotFoundError(f"Le fichier d'exemple {example_path} est introuvable")
    
    try:
        # Copie le fichier d'exemple
        with open(example_path, 'r', encoding='utf-8') as src, \
             open(destination, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
            
        console.print(f"[green]Configuration par défaut créée: {destination}")
        
    except Exception as e:
        console.print(f"[red]Erreur lors de la création de la configuration: {e}")


__all__ = [
    'SiteConfig',
    'SSHConfig',
    'FilesConfig',
    'DatabaseConfig',
    'BackupConfig',
    'load_config',
    'create_default_config',
]
