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
def backup() -> None:
    """Gestion des sauvegardes."""
    pass


@backup.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--output', '-o', type=click.Path(dir_okay=False, writable=True),
              help="Chemin de sortie de l'archive (par défaut: backups/backup-{timestamp}.tar.gz)")
@click.option('--passphrase', prompt=False, hide_input=True, default=None,
              help="Passphrase de la clé SSH (si elle en a une)")
def files(config_file: str, output: Optional[str], passphrase: Optional[str]) -> None:
    """Sauvegarde les fichiers d'un site web.
    
    CONFIG_FILE est le chemin vers le fichier de configuration
    """
    from datetime import datetime
    from backup_site.config import load_config
    from backup_site.utils.ssh import SSHKeyValidator
    from backup_site.backup.files import FileBackup
    import paramiko
    
    try:
        # Charge la configuration
        console.print("[cyan]Chargement de la configuration...[/]")
        config = load_config(Path(config_file))
        ssh_config = config.ssh
        files_config = config.files
        backup_config = config.backup
        
        # Valide les clés SSH
        console.print("[cyan]Validation des clés SSH...[/]")
        SSHKeyValidator.validate_key_file(ssh_config.private_key_path, "private")
        
        # Établit la connexion SSH
        console.print(f"[cyan]Connexion à {ssh_config.host}:{ssh_config.port}...[/]")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            key = SSHKeyValidator.load_private_key(ssh_config.private_key_path, passphrase)
            ssh_client.connect(
                hostname=ssh_config.host,
                port=ssh_config.port,
                username=ssh_config.user,
                pkey=key,
                timeout=30
            )
            print_success("Connexion SSH établie")
        except Exception as e:
            print_error(f"Impossible de se connecter: {e}")
        
        # Crée le gestionnaire de sauvegarde
        file_backup = FileBackup(
            ssh_client=ssh_client,
            remote_path=str(files_config.remote_path),
            include_patterns=files_config.include_patterns,
            exclude_patterns=files_config.exclude_patterns,
        )
        
        # Détermine le chemin de sortie
        if output:
            output_path = Path(output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(backup_config.destination)
            output_path = backup_dir / f"backup_{timestamp}.tar.gz"
        
        # Lance la sauvegarde
        console.print(f"\n[cyan]Sauvegarde des fichiers...[/]")
        console.print(f"[dim]Chemin distant: {files_config.remote_path}[/]")
        console.print(f"[dim]Patterns d'inclusion: {len(files_config.include_patterns)}[/]")
        console.print(f"[dim]Patterns d'exclusion: {len(files_config.exclude_patterns)}[/]")
        
        success, message, bytes_written = file_backup.backup_to_file(output_path)
        
        if success:
            console.print(f"\n{message}")
            console.print(f"[green]Archive créée: {output_path}[/]")
        
    except Exception as e:
        print_error(f"Erreur lors de la sauvegarde: {e}")
    finally:
        # Ferme la connexion SSH
        try:
            ssh_client.close()
        except:
            pass


@backup.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--output', '-o', type=click.Path(dir_okay=False, writable=True),
              help="Chemin de sortie du dump (par défaut: backups/database-{timestamp}.sql.gz)")
@click.option('--passphrase', prompt=False, hide_input=True, default=None,
              help="Passphrase de la clé SSH (si elle en a une)")
def database(config_file: str, output: Optional[str], passphrase: Optional[str]) -> None:
    """Sauvegarde la base de données MySQL.
    
    CONFIG_FILE est le chemin vers le fichier de configuration
    """
    from datetime import datetime
    from backup_site.config import load_config
    from backup_site.utils.ssh import SSHKeyValidator
    from backup_site.backup.database import DatabaseBackup
    import paramiko
    
    try:
        # Charge la configuration
        console.print("[cyan]Chargement de la configuration...[/]")
        config = load_config(Path(config_file))
        ssh_config = config.ssh
        db_config = config.database
        backup_config = config.backup
        
        # Valide les clés SSH
        console.print("[cyan]Validation des clés SSH...[/]")
        SSHKeyValidator.validate_key_file(ssh_config.private_key_path, "private")
        
        # Établit la connexion SSH
        console.print(f"[cyan]Connexion à {ssh_config.host}:{ssh_config.port}...[/]")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            key = SSHKeyValidator.load_private_key(ssh_config.private_key_path, passphrase)
            ssh_client.connect(
                hostname=ssh_config.host,
                port=ssh_config.port,
                username=ssh_config.user,
                pkey=key,
                timeout=30
            )
            print_success("Connexion SSH établie")
        except Exception as e:
            print_error(f"Impossible de se connecter: {e}")
        
        # Crée le gestionnaire de sauvegarde BDD
        db_backup = DatabaseBackup(
            ssh_client=ssh_client,
            db_host=db_config.host,
            db_port=db_config.port,
            db_name=db_config.name,
            db_user=db_config.user,
            db_password=db_config.password.get_secret_value(),
            compress=True,
            ssl_enabled=False,
        )
        
        # Détermine le chemin de sortie
        if output:
            output_path = Path(output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(backup_config.destination)
            output_path = backup_dir / f"database_{timestamp}.sql.gz"
        
        # Lance la sauvegarde
        console.print(f"\n[cyan]Sauvegarde de la base de données...[/]")
        console.print(f"[dim]Hôte: {db_config.host}:{db_config.port}[/]")
        console.print(f"[dim]Base: {db_config.name}[/]")
        console.print(f"[dim]Utilisateur: {db_config.user}[/]")
        
        success, message, bytes_written = db_backup.backup_to_file(output_path)
        
        if success:
            console.print(f"\n{message}")
            console.print(f"[green]Dump créé: {output_path}[/]")
        
    except Exception as e:
        print_error(f"Erreur lors de la sauvegarde BDD: {e}")
    finally:
        # Ferme la connexion SSH
        try:
            ssh_client.close()
        except:
            pass


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


@main.group()
def load() -> None:
    """Chargement des sauvegardes dans Docker local."""
    pass


@load.command()
@click.argument('archive_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--container', '-c', default='backup-test-wordpress',
              help="Nom du container Docker (défaut: backup-test-wordpress)")
@click.option('--path', '-p', default='/var/www/html',
              help="Chemin dans le container (défaut: /var/www/html)")
def files(archive_file: str, container: str, path: str) -> None:
    """Charge les fichiers depuis une archive tar.gz dans Docker local.
    
    ARCHIVE_FILE est le chemin vers l'archive tar.gz
    """
    from backup_site.docker_load.files import DockerFileLoad
    
    try:
        console.print("[cyan]Chargement des fichiers dans Docker...[/]")
        console.print(f"[dim]Container: {container}[/]")
        console.print(f"[dim]Archive: {archive_file}[/]")
        console.print(f"[dim]Destination: {path}[/]")
        
        # Crée le gestionnaire de chargement Docker
        file_load = DockerFileLoad(
            container_name=container,
            remote_path=path,
        )
        
        # Lance le chargement
        success, message = file_load.load_from_file(Path(archive_file))
        
        if success:
            console.print(f"\n{message}")
            console.print(f"[green]Chargement réussi![/]")
        
    except Exception as e:
        print_error(f"Erreur lors du chargement: {e}")


@load.command()
@click.argument('dump_file', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--container', '-c', default='backup-test-mysql',
              help="Nom du container MySQL/MariaDB Docker (défaut: backup-test-mysql)")
@click.option('--wordpress-container', '-w', default='backup-test-wordpress',
              help="Nom du container WordPress (pour extraire les infos via wp-cli, défaut: backup-test-wordpress)")
@click.option('--db-name', '-d', default=None,
              help="Nom de la base de données (optionnel si wordpress-container fourni)")
@click.option('--db-user', '-u', default=None,
              help="Utilisateur de la base de données (optionnel si wordpress-container fourni)")
@click.option('--db-password', '-p', default=None,
              help="Mot de passe de la base de données (optionnel si wordpress-container fourni)")
def database(dump_file: str, container: str, wordpress_container: str, db_name: Optional[str], db_user: Optional[str], db_password: Optional[str]) -> None:
    """Charge la base de données MySQL depuis un dump dans Docker local.
    
    DUMP_FILE est le chemin vers le fichier dump (SQL ou SQL.GZ)
    
    Les infos de la BDD sont extraites automatiquement depuis wp-config.php via wp-cli.
    Vous pouvez les spécifier manuellement avec --db-name, --db-user, --db-password.
    """
    from backup_site.docker_load.database import DockerDatabaseLoad
    
    try:
        console.print("[cyan]Chargement de la base de données dans Docker...[/]")
        console.print(f"[dim]Container MySQL: {container}[/]")
        console.print(f"[dim]Container WordPress: {wordpress_container}[/]")
        console.print(f"[dim]Dump: {dump_file}[/]")
        
        # Crée le gestionnaire de chargement Docker BDD
        db_load = DockerDatabaseLoad(
            container_name=container,
            wordpress_container=wordpress_container,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
        )
        
        # Lance le chargement
        success, message = db_load.load_from_file(Path(dump_file))
        
        if success:
            console.print(f"\n{message}")
            console.print(f"[green]Chargement réussi![/]")
        
    except Exception as e:
        print_error(f"Erreur lors du chargement BDD: {e}")


@load.command()
@click.option('--container', '-c', default='backup-test-wordpress',
              help="Nom du container WordPress Docker (défaut: backup-test-wordpress)")
@click.option('--old-url', '-o', required=True,
              help="Ancienne URL (ex: https://www.feelgoodbymelanie.com)")
@click.option('--new-url', '-n', required=True,
              help="Nouvelle URL (ex: http://localhost:8080)")
def setup(container: str, old_url: str, new_url: str) -> None:
    """Configure WordPress pour Docker local après chargement.
    
    Utilise wp-cli pour :
    - Configurer le système de fichiers (FS_METHOD = 'direct')
    - Mettre à jour siteurl et home
    - Faire un search-replace sur le contenu
    """
    from backup_site.docker_load.wordpress import DockerWordPressAdapter
    
    try:
        console.print("[cyan]Configuration de WordPress pour Docker local...[/]")
        console.print(f"[dim]Container: {container}[/]")
        console.print(f"[dim]Ancien URL: {old_url}[/]")
        console.print(f"[dim]Nouveau URL: {new_url}[/]")
        
        # Crée l'adaptateur WordPress
        adapter = DockerWordPressAdapter(
            container_name=container,
            old_url=old_url,
            new_url=new_url,
        )
        
        # Configure WordPress
        success, message = adapter.setup()
        
        if success:
            console.print(f"\n{message}")
            
            # Vérifie la configuration
            console.print("\n[cyan]Vérification de la configuration...[/]")
            success, verify_msg = adapter.verify()
            console.print(f"\n{verify_msg}")
            console.print(f"[green]Configuration réussie![/]")
        
    except Exception as e:
        print_error(f"Erreur lors de la configuration: {e}")


# Alias pour compatibilité
@load.command(name="adapt-urls")
@click.option('--container', '-c', default='backup-test-wordpress',
              help="Nom du container WordPress Docker (défaut: backup-test-wordpress)")
@click.option('--old-url', '-o', required=True,
              help="Ancienne URL (ex: https://www.feelgoodbymelanie.com)")
@click.option('--new-url', '-n', required=True,
              help="Nouvelle URL (ex: http://localhost:8080)")
def adapt_urls(container: str, old_url: str, new_url: str) -> None:
    """Alias deprecated pour 'setup'. Utiliser 'setup' à la place."""
    console.print("[yellow]⚠️  adapt-urls est deprecated, utiliser 'setup' à la place[/]")
    setup(container, old_url, new_url)


if __name__ == "__main__":
    main()
