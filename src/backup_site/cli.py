"""Interface en ligne de commande pour Backup Site."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Configuration du logger
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

console = Console()


def print_error(message: str) -> None:
    """Affiche un message d'erreur formaté."""
    console.print(f"[bold red]Erreur:[/] {message}")
    sys.exit(1)


def print_success(message: str) -> None:
    """Affiche un message de succès formaté."""
    console.print(f"[bold green]✓[/] {message}")


@click.group()
@click.version_option()
@click.option('--verbose', '-v', is_flag=True, help="Active les logs détaillés")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """Backup Site - Solution de sauvegarde pour sites web."""
    # Configure le niveau de log
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Mode verbeux activé")
    
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose


@main.command()
def version() -> None:
    """Affiche la version de l'application."""
    from backup_site import __version__, __description__
    
    console.print(Panel.fit(
        f"[bold blue]Backup Site[/] [green]v{__version__}[/]\n"
        f"{__description__}",
        title="Backup Site",
        border_style="blue"
    ))


@main.group()
def config() -> None:
    """Gestion des configurations de sauvegarde."""
    pass


@config.command()
@click.argument('output', type=click.Path(dir_okay=False, writable=True), default='config/site.yaml')
def init(output: str) -> None:
    """Initialise un nouveau fichier de configuration.
    
    OUTPUT est le chemin où enregistrer la configuration (par défaut: config/site.yaml)
    """
    from backup_site.config import create_default_config
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        create_default_config(output_path)
        print_success(f"Configuration initialisée dans {output_path}")
    except Exception as e:
        print_error(f"Impossible de créer la configuration: {e}")




@config.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--show-secrets', is_flag=True, help="Affiche les informations sensibles")
def validate(config_file: str, show_secrets: bool) -> None:
    """Valide un fichier de configuration.
    
    CONFIG_FILE est le chemin vers le fichier de configuration à valider
    """
    from backup_site.config import load_config, SiteConfig
    
    try:
        config = load_config(Path(config_file))
        
        # Affiche un résumé de la configuration
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Section", style="cyan")
        table.add_column("Paramètres")
        
        # Section Site
        site_info = "\n".join(f"{k}: {v}" for k, v in config.site.items())
        table.add_row("Site", site_info)
        
        # Section SSH
        ssh = config.ssh
        ssh_info = f"""
        Host: {ssh.host}
        User: {ssh.user}
        Port: {ssh.port}
        Clé privée: {ssh.private_key_path}
        """.strip()
        table.add_row("SSH", ssh_info)
        
        # Section Fichiers
        files = config.files
        files_info = f"""
        Chemin distant: {files.remote_path}
        Inclusions: {', '.join(files.include_patterns[:3])}...
        Exclusions: {', '.join(files.exclude_patterns[:3])}...
        """.strip()
        table.add_row("Fichiers", files_info)
        
        # Section Base de données
        db = config.database
        db_password = db.password.get_secret_value() if show_secrets else "***"
        db_info = f"""
        Hôte: {db.host}
        Port: {db.port}
        Base: {db.name}
        Utilisateur: {db.user}
        Mot de passe: {db_password}
        """.strip()
        table.add_row("Base de données", db_info)
        
        # Section Backup
        backup = config.backup
        backup_info = f"""
        Destination: {backup.destination}
        Compression: {backup.compression}
        Rétention: {backup.retention_days} jours
        """.strip()
        table.add_row("Sauvegarde", backup_info)
        
        console.print("\n[bold green]✓ Configuration valide[/]")
        console.print(table)
        
    except Exception as e:
        print_error(f"Configuration invalide: {e}")


@main.group()
def ssh() -> None:
    """Gestion des clés SSH et connexions."""
    pass


@ssh.command()
def setup_guide() -> None:
    """Affiche un guide pour configurer les clés SSH avec FOURNISSEUR_HEBERGEMENT."""
    from backup_site.utils.ssh import print_ssh_setup_guide
    
    print_ssh_setup_guide()


@ssh.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--passphrase', prompt=False, hide_input=True, default=None,
              help="Passphrase de la clé SSH (si elle en a une)")
def test(config_file: str, passphrase: Optional[str]) -> None:
    """Teste la connexion SSH avec les paramètres de la configuration.
    
    CONFIG_FILE est le chemin vers le fichier de configuration à tester
    """
    from backup_site.config import load_config
    from backup_site.utils.ssh import SSHKeyValidator
    
    try:
        # Charge la configuration
        config = load_config(Path(config_file))
        ssh_config = config.ssh
        
        console.print("[cyan]Validation des clés SSH...[/]")
        
        # Valide la clé privée
        try:
            SSHKeyValidator.validate_key_file(ssh_config.private_key_path, "private")
            print_success("Clé privée valide")
        except Exception as e:
            print_error(f"Clé privée invalide: {e}")
        
        # Valide la clé publique si elle existe
        if ssh_config.public_key_path:
            try:
                SSHKeyValidator.validate_key_file(ssh_config.public_key_path, "public")
                print_success("Clé publique valide")
            except Exception as e:
                console.print(f"[yellow]Attention:[/] {e}")
        
        # Teste la connexion SSH
        console.print("\n[cyan]Test de la connexion SSH...[/]")
        success, message = SSHKeyValidator.test_ssh_connection(
            host=ssh_config.host,
            username=ssh_config.user,
            key_path=ssh_config.private_key_path,
            port=ssh_config.port,
            passphrase=passphrase
        )
        
        if success:
            print_success(message)
            console.print("\n[bold green]✓ Connexion SSH fonctionnelle![/]")
        else:
            print_error(message)
            
    except Exception as e:
        print_error(f"Erreur lors du test SSH: {e}")


if __name__ == "__main__":
    main()
