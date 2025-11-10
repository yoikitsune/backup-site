"""Module d'adaptation de la configuration WordPress pour Docker local.

Stratégie :
- Utilise wp-cli pour adapter les URLs
- Fait un search-replace sur le contenu
- Pas de SSH, accès direct au container Docker via docker exec

Flux :
  1. Adapter siteurl et home avec wp-cli
  2. Faire search-replace sur le contenu
  3. Vérifier que tout fonctionne
"""

import logging
import subprocess
from typing import Tuple

logger = logging.getLogger(__name__)


class DockerWordPressAdapter:
    """Gère l'adaptation de la configuration WordPress pour Docker local."""
    
    def __init__(
        self,
        container_name: str,
        old_url: str,
        new_url: str,
    ):
        """Initialise l'adaptateur WordPress.
        
        Args:
            container_name: Nom du container WordPress Docker
            old_url: Ancienne URL (ex: https://www.feelgoodbymelanie.com)
            new_url: Nouvelle URL (ex: http://localhost:8080)
        """
        self.container_name = container_name
        self.old_url = old_url
        self.new_url = new_url
    
    def _run_wp_cli_command(self, *args) -> str:
        """Exécute une commande wp-cli dans le container.
        
        Args:
            *args: Arguments de la commande wp-cli
            
        Returns:
            Sortie de la commande
            
        Raises:
            RuntimeError: Si la commande échoue
        """
        cmd = ["docker", "exec", self.container_name, "wp", "--allow-root"] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur wp-cli: {e.stderr}")
    
    def _configure_filesystem(self) -> None:
        """Configure le système de fichiers WordPress pour permettre les mises à jour.
        
        Étapes :
        1. Ajoute `define( 'FS_METHOD', 'direct' );` au wp-config.php
        2. Corrige les permissions des dossiers uploads/
        
        Raises:
            RuntimeError: Si la configuration échoue
        """
        try:
            logger.debug(f"Configuration du système de fichiers")
            
            # Étape 1 : Vérifier si FS_METHOD est déjà configuré (en essayant de le lire)
            try:
                result = self._run_wp_cli_command("config", "get", "FS_METHOD")
                if result and result != "":
                    logger.info(f"FS_METHOD déjà configuré: {result}")
                else:
                    raise RuntimeError("FS_METHOD vide")
            except RuntimeError:
                # FS_METHOD n'existe pas, c'est normal, on va l'ajouter
                logger.debug("FS_METHOD n'existe pas encore, ajout en cours...")
                
                # Ajouter FS_METHOD au wp-config.php
                # On l'ajoute avant la ligne "That's all, stop editing!"
                cmd = [
                    "docker", "exec", self.container_name, "bash", "-c",
                    "sed -i \"/That's all, stop editing/i define( 'FS_METHOD', 'direct' );\" /var/www/html/wp-config.php"
                ]
                
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                logger.info(f"✓ FS_METHOD configuré")
            
            # Étape 2 : Corriger les permissions de wp-content/ pour que www-data puisse écrire
            logger.debug("Correction des permissions de wp-content/")
            
            # Changer l'owner en www-data:www-data pour tout wp-content/
            # Cela permet à WordPress (qui s'exécute en tant que www-data) d'écrire partout
            cmd_chown = [
                "docker", "exec", self.container_name, "bash", "-c",
                "chown -R www-data:www-data /var/www/html/wp-content"
            ]
            
            subprocess.run(
                cmd_chown,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Dossiers : 755 (rwxr-xr-x) - sauf uploads qui doit être 777
            cmd_dirs = [
                "docker", "exec", self.container_name, "bash", "-c",
                "find /var/www/html/wp-content -type d ! -path '*/uploads*' -exec chmod 755 {} \\;"
            ]
            
            subprocess.run(
                cmd_dirs,
                check=True,
                capture_output=True,
                text=True
            )
            
            # uploads/ : 777 (rwxrwxrwx) - writable par tout le monde
            cmd_uploads_dirs = [
                "docker", "exec", self.container_name, "bash", "-c",
                "find /var/www/html/wp-content/uploads -type d -exec chmod 777 {} \\;"
            ]
            
            subprocess.run(
                cmd_uploads_dirs,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Fichiers : 644 (rw-r--r--)
            cmd_files = [
                "docker", "exec", self.container_name, "bash", "-c",
                "find /var/www/html/wp-content -type f -exec chmod 644 {} \\;"
            ]
            
            subprocess.run(
                cmd_files,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"✓ Permissions de wp-content/ corrigées (owner = www-data, uploads/ = 777)")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la configuration du filesystem: {e.stderr}")
    
    def setup(self) -> Tuple[bool, str]:
        """Configure WordPress pour Docker local.
        
        Étapes :
        1. Configurer le système de fichiers (FS_METHOD + permissions)
        2. Configurer la connexion à la base de données Docker
        3. Mettre à jour siteurl
        4. Mettre à jour home
        5. Faire search-replace sur le contenu
        
        Returns:
            Tuple (succès, message)
            
        Raises:
            RuntimeError: Si une commande échoue
        """
        try:
            logger.info(f"Configuration de WordPress pour Docker local")
            logger.info(f"  Ancien URL : {self.old_url}")
            logger.info(f"  Nouveau URL : {self.new_url}")
            
            # Étape 1 : Configurer le système de fichiers
            logger.debug(f"Étape 1 : Configuration du système de fichiers")
            self._configure_filesystem()
            
            # Étape 2 : Configurer la connexion à la base de données Docker
            logger.debug(f"Étape 2 : Configuration de la base de données")
            # Mettre à jour DB_HOST pour pointer vers le container MySQL Docker
            cmd = [
                "docker", "exec", self.container_name, "bash", "-c",
                "sed -i \"s/define( 'DB_HOST', '[^']*' );/define( 'DB_HOST', 'backup-test-mysql' );/\" /var/www/html/wp-config.php"
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"✓ DB_HOST configuré pour Docker")
            
            # Étape 3 : Mettre à jour siteurl
            logger.debug(f"Étape 3 : Mise à jour de siteurl")
            self._run_wp_cli_command("option", "update", "siteurl", self.new_url)
            logger.info(f"✓ siteurl mis à jour")
            
            # Étape 4 : Mettre à jour home
            logger.debug(f"Étape 4 : Mise à jour de home")
            self._run_wp_cli_command("option", "update", "home", self.new_url)
            logger.info(f"✓ home mis à jour")
            
            # Étape 5 : Faire search-replace sur le contenu
            logger.debug(f"Étape 5 : Search-replace sur le contenu")
            self._run_wp_cli_command(
                "search-replace",
                self.old_url,
                self.new_url,
                "--all-tables",
                "--skip-columns=guid"
            )
            logger.info(f"✓ Search-replace complété")
            
            message = (
                f"✓ Configuration de WordPress réussie\n"
                f"  Container: {self.container_name}\n"
                f"  Ancien URL: {self.old_url}\n"
                f"  Nouveau URL: {self.new_url}\n"
                f"  Filesystem: FS_METHOD = 'direct' configuré\n"
                f"  Permissions: uploads/ corrigées"
            )
            logger.info(message)
            
            return True, message
            
        except RuntimeError as e:
            error_msg = f"Erreur lors de la configuration: {str(e)}"
            logger.error(error_msg)
            raise
    
    def adapt_urls(self) -> Tuple[bool, str]:
        """Adapte les URLs WordPress pour Docker local (alias pour setup).
        
        Deprecated: Utiliser setup() à la place.
        
        Returns:
            Tuple (succès, message)
        """
        logger.warning("adapt_urls() est deprecated, utiliser setup() à la place")
        return self.setup()
    
    def verify(self) -> Tuple[bool, str]:
        """Vérifie que l'adaptation a fonctionné.
        
        Returns:
            Tuple (succès, message)
            
        Raises:
            RuntimeError: Si la vérification échoue
        """
        try:
            logger.info(f"Vérification de l'adaptation")
            
            # Vérifier siteurl
            siteurl = self._run_wp_cli_command("option", "get", "siteurl")
            logger.debug(f"siteurl: {siteurl}")
            
            # Vérifier home
            home = self._run_wp_cli_command("option", "get", "home")
            logger.debug(f"home: {home}")
            
            # Vérifier que les URLs correspondent
            if siteurl != self.new_url or home != self.new_url:
                raise RuntimeError(f"Les URLs ne correspondent pas: siteurl={siteurl}, home={home}")
            
            message = (
                f"✓ Vérification réussie\n"
                f"  siteurl: {siteurl}\n"
                f"  home: {home}"
            )
            logger.info(message)
            
            return True, message
            
        except RuntimeError as e:
            error_msg = f"Erreur lors de la vérification: {str(e)}"
            logger.error(error_msg)
            raise
